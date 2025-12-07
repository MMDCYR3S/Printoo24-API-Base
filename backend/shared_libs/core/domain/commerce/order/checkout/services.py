import uuid
from django.db import transaction
from django.core.files.base import ContentFile
from core.models import Order, OrderItem, OrderItemFile, OrderStatus
from core.domain.commerce.cart import CartRepository
from ..main.repositories import OrderRepository

class CheckoutDomainService:
    def __init__(self):
        self._order_repo = OrderRepository()
        self._cart_repo = CartRepository()

    def _generate_order_code(self):
        """ تولید کد پیگیری خوانا و یکتا """
        return str(uuid.uuid4().hex[:8]).upper()

    @transaction.atomic
    def checkout_cart(self, user, address, order_type: str) -> Order:
        cart = self._cart_repo.get_cart_by_user(user)
        if not cart or not cart.cart_items.exists():
            raise ValueError("سبد خرید خالی است.")

        # ===== محاسبه قیمت کل ===== #
        cart_items = cart.cart_items.select_related('product').prefetch_related('uploads').all()
        base_price = sum(item.price for item in cart_items)

        # ===== دریافت وضعیت اولیه ===== #
        initial_status = OrderStatus.objects.get_or_create(
            name='در حال بررسی',
            internal_code='PENDING'
        )

        # ===== ایجاد سفارش ===== #
        order = self._order_repo.create_order_shell({
            "user": user,
            "order_code": self._generate_order_code(),
            "type": order_type,
            "current_status": initial_status,
            "address": address,
            "base_products_price": base_price,
            "total_price": base_price,
        })

        # ===== انتقال آیتم ها ===== #
        for c_item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=c_item.product,
                quantity=c_item.quantity,
                unit_price=c_item.product.base_price if hasattr(c_item.product, 'base_price') else 0, # قیمت واحد مهم است
                price=c_item.price,
                items=c_item.items,
            )

            # ===== انتقال فایل‌های طراحی ===== #
            for upload in c_item.uploads.all():
                if upload.file:
                    # ===== انتقال فایل ===== #
                    new_file_content = ContentFile(upload.file.read())
                    new_file_content.name = upload.file.name.split('/')[-1]
                    
                    OrderItemFile.objects.create(
                        order_item=order_item,
                        requirement=upload.requirement,
                        file=new_file_content,
                        version=1,
                        is_latest=True,
                        status='pending'
                    )
        # ===== پاکسازی سبد خرید ===== #
        cart.delete()
        
        return order