import uuid
from decimal import Decimal
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

    def _generate_order_code(self, phone_number="UNK"):
        """ تولید کد پیگیری خوانا و یکتا """
        return f"ORD-{str(uuid.uuid4().hex[:8]).upper()}-{str(phone_number[:5]).upper()}"
    
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
            initial_status = OrderStatus.objects.get(internal_code="PENDING_PROGRESS_ADMIN")
        except OrderStatus.DoesNotExist:
            initial_status = OrderStatus.objects.first()
            
        phone_number = user.phone_number if user else "UNK"

        quantity = cart_item.quantity or 1

        # ===== دریافت پیش‌فاکتورِ مرتبط با آیتم سبد خرید ===== #
        # پیش‌فاکتورها هنگام افزودن آیتم به سبد خرید (سیگنال cart) ساخته می‌شوند و
        # حالا باید بدون ساخت نمونهٔ تکراری، به سفارش تبدیل شوند.
        quotation = Quotation.objects.filter(cart_item=cart_item).first()

        # قیمت پایه از پیش‌فاکتور گرفته می‌شود (صاحب قیمت، پیش‌فاکتور است).
        base_total = cart_item.price
        if quotation and quotation.total_price:
            base_total = quotation.total_price

        unit_price = base_total / Decimal(quantity) if quantity else base_total

        # ===== ایجاد سفارش ===== #
        order = Order.objects.create(
            user=user,
            current_status=initial_status,
            subtotal=base_total,
            total_price=base_total,
            base_products_price=base_total,
            type=final_order_type,
order_code=self._generate_order_code(phone_number=phone_number),
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            company_name=company_name,
            full_address=full_address_text,
            address=address_object
        )
        
        # ===== ایجاد آیتم سفارش ===== #
        order_item = OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=quantity,
            name=cart_item.name,
            price=unit_price,
            items=cart_item.items,
            description=cart_item.description,
            status='pending'
        )
        
        # ===== منطق تصویر محصول برای Quotation ===== #
        product_image_obj = cart_item.product.product_image.order_by('order').first()
        final_image_file = product_image_obj.image if product_image_obj else None
        
        # ===== تبدیل پیش‌فاکتور به سفارش ===== #
        # اتصال به سبد خرید حذف و به سفارش گره می‌خورد (طبق روند تعریف‌شده).
        if quotation:
            quotation.converted_order = order
            quotation.cart_item = None
            quotation.status = Quotation.Status.CONVERTED
            quotation.customer_name = recipient_name
            quotation.product_name = cart_item.product.name if cart_item.product else quotation.product_name
            quotation.product_image = final_image_file
            quotation.product_snapshot = cart_item.items
            quotation.quantity = quantity
            quotation.total_price = base_total
            quotation.valid_until = None
            quotation.save()
        else:
            # اگر به هر دلیلی پیش‌فاکتورِ مرتبط ساخته نشده بود، می‌سازیم.
            Quotation.objects.create(
                quotation_number=f"QUOT-{order.order_code}",
                converted_order=order,
                customer_name=recipient_name,
                product_name=cart_item.product.name if cart_item.product else "محصول حذف شده",
                product_image=final_image_file,
                product_snapshot=cart_item.items,
                quantity=quantity,
                total_price=base_total,
                status=Quotation.Status.CONVERTED,
                created_at=timezone.now(),
            )

        # ===== انتقال فایل‌های طراحی ===== #
        self._transfer_files(cart_item, order_item)
        
        # ===== حذف آیتم از سبد خرید ===== #
        cart_item.delete()
        
        return order
