from typing import Optional, Dict

from decimal import Decimal
from django.db import transaction

from core.models import (
    Cart,
    CartItem,
    CartItemUpload,
    Product,
    ProductFileUploadRequirement,
    User,
)
from core.domain.product import ProductPriceCalculator
from shared_libs.core.domain.cart.exceptions import (
    InvalidQuantityException,
    ItemNotFoundException,
)
from .repositories import CartRepository, CartItemRepository

# ======= Cart Domain Service ======= #
class CartDomainService:
    """
    سرویس برای مدیریت عملیات‌های اصلی سبد خرید.
    """
    def __init__(self, cart_repo: Optional[CartRepository] = None, item_repo: Optional[CartItemRepository] = None):
        self._cart_repo = cart_repo or CartRepository()
        self._item_repo = item_repo or CartItemRepository()

    # ===== دریافت یا ساخت سبد خرید برای کاربر ===== #
    def get_or_create_cart_for_user(self, user: User) -> Cart:
        """
        سبد خرید یک کاربر را برمی‌گرداند. اگر وجود نداشته باشد، یکی جدید می‌سازد.
        ورودی این متد همیشه یک کاربر معتبر است.
        """
        if not user.is_authenticated:
            raise ValueError("کاربر احراز هویت نشده است.")
        
        cart = self._cart_repo.get_or_create_cart(user)
        if not cart:
            cart = self._cart_repo.create({"user": user})
        return cart
    
    # ===== جستجوی آیتم در سبد خرید ===== #
    def find_item(self, cart: Cart, product: Product, items: Dict) -> Optional[CartItem]:
        return self._repository.find_item_in_cart(cart=cart, product=product, items=items)

    # ===== افزودن آیتم پیچیده به سبد خرید ===== #
    @transaction.atomic
    def add_complex_item(self, user: User, product: Product, quantity: int, 
                         specs: Dict, uploaded_files_map: Dict[int, str]) -> CartItem:
        """
        افزودن آیتم پیچیده (چاپ) به سبد خرید.
        
        Args:
            specs: شامل material, size, options, custom_dimensions
            uploaded_files_map: دیکشنری {requirement_id: file_path_relative_to_media}
        """
        # ===== اعتبارسنجی تعداد ===== #
        if quantity <= 0:
            raise InvalidQuantityException("تعداد باید بیشتر از صفر باشد.")
        
        # ===== محاسبه قیمت کل آیتم ===== #
        calculator = ProductPriceCalculator(
            product=product,
            quantity=specs['quantity_obj'], 
            material=specs['material_obj'],
            options=specs['options_objs'],
            size=specs.get('size_obj'),
            custom_dimensions=specs.get('custom_dimensions')
        )
        price_result = calculator.calculate()
        final_price = Decimal(str(price_result['final_price']))
        
        # ===== ایجاد یا دریافت سبد خرید ===== #
        cart = self._cart_repo.get_or_create_cart(user)
        
        # ===== ایجاد آیتم سبد خرید ===== #
        cart_item = self._item_repo.create({
            "cart": cart,
            "product": product,
            "quantity": quantity,
            "price": final_price,
            "items": specs
        })
        
        # ===== افزودن فایل‌های آپلود شده به آیتم سبد خرید ===== #
        for req_id, file_path in uploaded_files_map.items():
            requirement = ProductFileUploadRequirement.objects.get(id=req_id)
            
            CartItemUpload.objects.create(
                cart_item=cart_item,
                requirement=requirement,
                file=file_path
            )

        return cart_item
    
    # ===== به‌روزرسانی تعداد آیتم در سبد خرید ===== #
    def update_item_quantity(self, item: CartItem, new_quantity: int) -> CartItem:
        if new_quantity <= 0:
            self._item_repo.delete(item)
            return None
            
        return self._item_repo.update(item, {"quantity": new_quantity})

    # ===== حذف آیتم با چک کردن مالکیت ===== #
    def remove_item(self, user: User, item_id: int):
        """
        حذف با چک کردن مالکیت (Security)
        """
        item = self._item_repo.get_item_details(item_id, user)
        if not item:
            raise ItemNotFoundException("آیتم یافت نشد یا متعلق به شما نیست.")
        self._item_repo.delete(item)
