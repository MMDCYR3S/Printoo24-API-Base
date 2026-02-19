import logging
from typing import List
from django.db import transaction
from rest_framework.exceptions import ValidationError 

from ..exceptions import EmptyCartError, ItemNotFoundException
from core.models import User, Address, Order, CustomerProfile
from apps.cart.models import Cart, CartItem
from apps.accounts.services import WalletService
from apps.order.domain_services import CheckoutService

logger = logging.getLogger('shop.services.order_creation')

class CreateOrderFromCartService:
    def __init__(self):
        self._checkout_domain = CheckoutService() 
        self._wallet_service = WalletService()
        
    def _construct_full_address(self, data: dict, address_obj: Address = None) -> str:
        """
        تجمیع آدرس در یک رشته واحد.
        فرمت: استان - شهر - آدرس دقیق - کدپستی: ...
        """
        if address_obj:
            # ===== دریافت اطلاعات مربوط به آدرس کاربر ===== #
            province = address_obj.province.name
            city = address_obj.city.name
            addr_text = address_obj.address
            postal = address_obj.postal_code
        else:
            # ===== اگر اطلاعات به صورت دستی بود ===== #
            province = data.get('province_name')
            city = data.get('city_name')
            addr_text = data.get('address_text')
            postal = data.get('postal_code', '---')
        
        # ===== اعتبارسنجی وجود اطلاعات ===== #
        if not (province and city and addr_text):
            raise ValidationError("استان، شهر و آدرس دقیق الزامی هستند.")

        return f"{province} - {city} - {addr_text} - کدپستی: {postal}"
    
    def _handle_address_logic(self, user: User, data: dict) -> Address:
        """
        مدیریت هوشمند آدرس:
        1. اگر address_id باشد، همان را برمی‌گرداند.
        2. اگر اطلاعات جدید باشد، چک می‌کند تکراری نباشد، اگر نبود می‌سازد.
        """
        address_id = data.get('address_id')
        
        # ===== انتخاب آدرس ===== #
        if address_id:
            try:
                return Address.objects.get(id=address_id, user=user)
            except Address.DoesNotExist:
                raise ValidationError("آدرس انتخاب شده نامعتبر است.")

        # ===== دریافت اطلاعات کاربر ===== #
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        postal_code = data.get('postal_code', '')
        address_text = data.get('address_text')

        if not (province_id and city_id and address_text):
             raise ValidationError("در صورت عدم انتخاب آدرس، وارد کردن استان، شهر و نشانی الزامی است.")
        
        # ===== بررسی وجود آدرس قدیمی ===== #
        existing_address = Address.objects.filter(
            user=user,
            province_id=province_id,
            city_id=city_id,
            address=address_text,
            postal_code=postal_code
        ).first()

        if existing_address:
            return existing_address

        # ===== ثبت آدرس جدید ===== #
        new_address = Address.objects.create(
            user=user,
            province_id=province_id,
            city_id=city_id,
            address=address_text,
            postal_code=postal_code
        )
        return new_address

    def _sync_user_profile(self, user: User, data: dict) -> dict:
        """
        1. اطلاعات را از ورودی می‌خواند.
        2. اگر پروفایل کاربر ناقص بود، آن را پر می‌کند.
        3. خروجی نهایی برای ثبت در سفارش را برمی‌گرداند.
        """
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone_number')
        company = data.get('company_name', '')

        if not (first_name and last_name and phone_number):
             raise ValidationError("نام، نام خانوادگی و شماره تماس الزامی است.")

        # ===== دریافت اطلاعات کاربر ===== #
        profile, created = CustomerProfile.objects.get_or_create(user=user, defaults={
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': phone_number,
            'company': company
        })

        if not created:
            # ===== آپدیت اطلاعات کاربر ===== #
            updated = False
            if not profile.first_name:
                profile.first_name = first_name
                updated = True
            if not profile.last_name:
                profile.last_name = last_name
                updated = True
            if not profile.phone_number:
                profile.phone_number = phone_number
                updated = True
            if not profile.company and company:
                profile.company = company
                updated = True
            
            if updated:
                profile.save()

        # ===== بازگردانی اطلاعات کاربر ===== #
        return {
            'recipient_name': f"{first_name} {last_name}",
            'recipient_phone': phone_number,
            'company_name': company
        }
        
    @transaction.atomic
    @transaction.atomic
    def execute(self, checkout_data: dict, cart_item_id: int, user: User = None, session_key: str = None) -> Order:
        """
        اجرای سفارش تکی.
        """
        logger.info(f"Checkout request. User: {user if user else 'GUEST'}")

        # ===== مدیریت آدرس ها ===== #
        address_obj = None
        if user and user.is_authenticated:
            address_obj = self._handle_address_logic(user, checkout_data)
        
        final_full_address = self._construct_full_address(checkout_data, address_obj)

        # ===== ارسال اطلاعات مشتری ===== #
        address_obj = None
        if user and user.is_authenticated:
            address_obj = self._handle_address_logic(user, checkout_data)
            profile_data = self._sync_user_profile(user, checkout_data) 
            recipient_name = profile_data['recipient_name']
            recipient_phone = profile_data['recipient_phone']
        else:
            recipient_name = f"{checkout_data.get('first_name')} {checkout_data.get('last_name')}"
            recipient_phone = checkout_data.get('phone_number')
        
        final_full_address = self._construct_full_address(checkout_data, address_obj)
        company_name = checkout_data.get('company_name')

        # ===== دریافت آیتم مربوطه ===== #
        try:
            if user:
                cart_item = CartItem.objects.get(id=cart_item_id, cart__user=user)
            elif session_key:
                cart_item = CartItem.objects.get(id=cart_item_id, cart__session_key=session_key)
            else:
                raise ItemNotFoundException("دسترسی غیرمجاز")
                
        except CartItem.DoesNotExist:
             raise ItemNotFoundException("آیتم سبد خرید یافت نشد.")

        if user and user.is_authenticated:
            user_balance = self._wallet_service.get_user_balance(user)
            if user_balance < cart_item.price:
                 logger.info(f"User {user.username} doesn't have enough balance but anyways... :)")
            self._wallet_service.debit(user=user, amount=cart_item.price)

        # ===== ایجاد سفارش مربوطه ===== #
        try:
            order = self._checkout_domain.checkout_single_item(
                user=user,
                cart_item=cart_item,
                order_type="1",
                full_address_text=final_full_address,
                address_object=address_obj,
                recipient_name=recipient_name,
                recipient_phone=recipient_phone,
                company_name=company_name
            )
            return order
        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            raise e

    @transaction.atomic
    def execute_bulk(self, checkout_data: dict, user: User = None, session_key: str = None, order_type: str = "1") -> List[Order]:
        """
        اجرای سفارش گروهی.
        """
        logger.info(f"Checkout Bulk. User: {user}, Session: {session_key}")
        logger.info(f"Start BULK checkout. User: {user if (user and user.is_authenticated) else 'GUEST'}")


        # ===== دریافت اطلاعات آدرس و اطلاعات کلی کاربر ===== #
        address_obj = None
        if user and user.is_authenticated:
            address_obj = self._handle_address_logic(user, checkout_data)
            profile_data = self._sync_user_profile(user, checkout_data)
            recipient_name = profile_data['recipient_name']
            recipient_phone = profile_data['recipient_phone']
        else:
            recipient_name = f"{checkout_data.get('first_name')} {checkout_data.get('last_name')}"
            recipient_phone = checkout_data.get('phone_number')
        
        # ===== ایجاد آدرس ===== #
        final_full_address = self._construct_full_address(checkout_data, address_obj)
        company_name = checkout_data.get('company_name')

        # ===== دریافت سبد خرید کاربر ===== #
        if user:
            cart = Cart.objects.filter(user=user).first()
        elif session_key:
            cart = Cart.objects.filter(session_key=session_key).first()
        else:
            raise EmptyCartError("سبد خرید یافت نشد.")

        if not cart or not cart.cart_items.exists():
            raise EmptyCartError("سبد خرید خالی است.")

        cart_items = list(cart.cart_items.select_related('product').prefetch_related('uploads').all())
        total_price = sum(item.price for item in cart_items)
        
        # ===== دریافت اطلاعات کلی کیف پول اگر کاربر لاگ شده باشد ===== #
        if user and user.is_authenticated:
            user_balance = self._wallet_service.get_user_balance(user)
            if user_balance < total_price:
                logger.info(f"User {user.username} doesn't have enough balance but anyways... :)")
            self._wallet_service.debit(user=user, amount=total_price)
            
        # ===== ایجاد سفارشات ===== #
        created_orders = []
        try:
            for cart_item in cart_items:
                order = self._checkout_domain.checkout_single_item(
                    user=user,
                    cart_item=cart_item,
                    order_type=order_type,
                    recipient_name=recipient_name,
                    recipient_phone=recipient_phone,
                    company_name=company_name,
                    full_address_text=final_full_address,
                    address_object=address_obj
                )
                created_orders.append(order)
                
            return created_orders
        except Exception as e:
            logger.error(f"Bulk checkout failed: {e}")
            raise e