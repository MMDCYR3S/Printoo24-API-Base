import uuid
from typing import List
from django.utils import timezone
from django.db import transaction
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError as DjangoValidationError

from core.order.models import Order, OrderItem, OrderItemFile, OrderStatus
from core.models import User, Address, Quotation
from apps.cart.models import CartItem

# ========== CHECKOUT SERVICE ========== #
class CheckoutService:
    """
    سرویس تبدیل سبد خرید به سفارش (Checkout Logic)
    """

    def _generate_order_code(self):
        """ تولید کد پیگیری خوانا و یکتا """
        return str(uuid.uuid4().hex[:8]).upper()
    
    def _transfer_files(self, cart_item: CartItem, order_item: OrderItem):
        """ ===== انتقال فایل‌های طراحی از Cart Item به Order Item ===== """
        for upload in cart_item.uploads.all():
            if upload.file:
                # ===== خواندن فایل های طراحی ===== #
                try:
                    upload.file.open()
                    file_content = ContentFile(upload.file.read())
                    file_name = upload.file.name.split('/')[-1]
                    upload.file.close()
                    # ===== ایجاد فایل در سیستم ===== #
                    OrderItemFile.objects.create(
                        order_item=order_item,
                        file=ContentFile(file_content.read(), name=file_name),
                        version=1,
                        is_latest=True
                    )
                except Exception as e:
                    raise e
                
    # ========== CHECKOUT SINGLE ITEM ========== #
    @transaction.atomic
    def checkout_single_item(
        self, 
        cart_item: CartItem, 
        # ===== داده‌های هویتی و آدرس ===== #
        recipient_name: str,
        recipient_phone: str,
        full_address_text: str,
        company_name: str = None,
        address_object: Address = None,
        user: User = None,
        order_type: str = "1"
    ) -> Order:
        """
        ایجاد سفارش.
        قانون دامنه: اگر user نال باشد، order_type باید حتما '2' (اختصاصی) باشد.
        """
        
        # ===== اگر کاربر مهمان بود، سفارش اختصاصی شود ===== #
        final_order_type = order_type
        if user is None:
            final_order_type = "2"
            
        # ===== دریافت وضعیت اولیه (باید از طریق کد سیستمی باشد) ===== #
        try:
            initial_status = OrderStatus.objects.get(internal_code="PENDING_INITIAL_ADMIN")
        except OrderStatus.DoesNotExist:
            initial_status = OrderStatus.objects.first()
            
            
        #‌ ===== ایجاد سفارش ===== #
        order = Order.objects.create(
            user=user,
            current_status=initial_status,
            total_price=cart_item.price,
            base_products_price=cart_item.price, 
            type=final_order_type,
            order_code=self._generate_order_code(),
            
            #‌ ===== نام و اطلاعات کاربر ===== #
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            company_name=company_name,
            #‌ ===== آدرس کاربر ===== #
            full_address=full_address_text,
            address_obj=address_object
        )
        
        # ===== ایجاد آیتم سفارش ===== #
        order_item = OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            name=cart_item.name,
            price=cart_item.price,
            items=cart_item.items,
            description=cart_item.description,
            status='pending'
        )
        
        # ===== پیدا کردن نام مشتری ===== #
        customer_name = user.username
        if hasattr(user, 'customer_profile'):
            customer_name = f"{user.customer_profile.first_name} {user.customer_profile.last_name}"
        
        # ===== منطق تصویر محصول برای Quotation ===== #
        product_image_obj = cart_item.product.product_image.order_by('order').first()
        final_image_file = product_image_obj.image if product_image_obj else None
        
        # ===== ایجاد پیش فاکتور برای سفارش ===== # 
        Quotation.objects.create(
            quotation_number=f"QUOT-{order.order_code}",
            converted_order=order,
            customer_name=recipient_name,
            product_name=cart_item.product.name if cart_item.product else "محصول حذف شده",
            product_image=final_image_file,
            product_snapshot=cart_item.items,
            quantity=cart_item.quantity,
            total_price=cart_item.price,
            status=Quotation.Status.CONVERTED,
            created_at=timezone.now(),
        )

        # ===== انتقال فایل‌های طراحی ===== #
        self._transfer_files(cart_item, order_item)
        
        # ===== حذف آیتم از سبد خرید ===== #
        cart_item.delete()
        
        return order
