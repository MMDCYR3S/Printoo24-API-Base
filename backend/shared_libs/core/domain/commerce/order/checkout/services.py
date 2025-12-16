import uuid
from typing import List
from django.utils import timezone
from django.db import transaction
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError as DjangoValidationError

from core.models import Order, OrderItem, OrderItemFile, OrderStatus, CartItem, Address, User, Quotation
from core.domain.commerce.cart import CartRepository
from core.domain.commerce.order import OrderRepository, OrderItemRepository

class CheckoutDomainService:
    def __init__(self):
        self._order_repo = OrderRepository()
        self._item_repo = OrderItemRepository()
        self._cart_repo = CartRepository()

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
                    new_file_content = ContentFile(upload.file.read())
                    upload.file.close()
                except Exception as e:
                    continue
                new_file_content.name = upload.file.name.split('/')[-1]
                
                # ===== ایجاد رکورد فایل جدید برای آیتم سفارش ===== #
                OrderItemFile.objects.create(
                    order_item=order_item,
                    requirement=upload.requirement,
                    file=new_file_content,
                    version=1,
                    is_latest=True
                )
    
    @transaction.atomic
    def checkout_single_item(self, user: User, cart_item: CartItem, address: Address, order_type: str) -> Order:
        """
        تبدیل یک CartItem مشخص به یک Order مجزا. (منطق جدید)
        """
        
      # ===== دریافت وضعیت اولیه (باید از طریق کد سیستمی باشد) =====
        try:
            initial_status = OrderStatus.objects.get(internal_code="PENDING_INITIAL_ADMIN")
        except OrderStatus.DoesNotExist:
            raise DjangoValidationError("خطای سیستمی: وضعیت اولیه سفارش مشخص نیست.")
        
        order = self._order_repo.create_order(
            user=user,
            order_code=self._generate_order_code(),
            order_type=order_type,
            order_status=initial_status,
            address=address,
            base_price=cart_item.price,
            total_price=cart_item.price,
        )
        # ===== ایجاد آیتم سفارش ===== #
        order_item = self._item_repo.create({
            "order": order,
            "product": cart_item.product,
            "quantity": cart_item.quantity,
            "price": cart_item.price,
            "items": cart_item.items,
        })
        
        product_image_obj = cart_item.product.product_image.filter(order=0).first()
        if not product_image_obj:
            product_image_obj = cart_item.product.product_image.first()
        final_image_file = product_image_obj.image if product_image_obj else None
        # ===== ایجاد پیش فاکتور ===== #
        Quotation.objects.create(
            quotation_number=f"QUOT-{order.order_code}",
            converted_order=order,
            customer_name=user.customer_profile.fullname() if user.customer_profile.first_name else 'نامشخص',
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
        
        self._item_repo.delete(cart_item)
        
        return order
