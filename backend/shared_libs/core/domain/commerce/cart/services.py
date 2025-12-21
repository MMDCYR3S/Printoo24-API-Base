from typing import Optional, Dict, Tuple

from decimal import Decimal
from django.db import transaction

from core.models import (
    Cart,
    CartItem,
    CartItemUpload,
    Product,
    ProductSize,
    User,
    ProductOptionValue
)
from core.domain.catalog.product import ProductPriceCalculator
from core.domain.commerce.cart.exceptions import (
    InvalidQuantityException,
    ItemNotFoundException,
)
from .repositories import CartRepository, CartItemRepository

# ======= Cart Domain Service ======= #
class CartDomainService:
    """
    سرویس برای مدیریت عملیات‌های اصلی سبد خرید.
    """
    def __init__(self):
        self._cart_repo = CartRepository()
        self._item_repo = CartItemRepository()

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
        return self._item_repo.find_item_in_cart(cart=cart, product=product, items=items)
    
    def get_item_details(self, cart: Cart) -> Dict:
        return self._item_repo.get_items_by_cart(cart)
    
    # ===== متد کمکی برای استخراج ابعاد ===== #
    def _resolve_dimensions(self, specs: Dict) -> Tuple[float, float]:
        """
        تشخیص طول و عرض بر اساس اینکه کاربر سایز استاندارد انتخاب کرده یا ابعاد دلخواه.
        """
        size_obj: Optional[ProductSize] = specs.get('size_obj')
        custom_dims = specs.get('custom_dimensions')

        if size_obj:
            return size_obj.size.width, size_obj.size.height
        
        if custom_dims:
            return float(custom_dims.get('width', 0)), float(custom_dims.get('height', 0))
            
        raise ValueError("ابعاد محصول مشخص نیست (نه سایز استاندارد، نه ابعاد دلخواه).")

    # ===== متد افزودن اصلاح شده (بدون فایل) ===== #
    @transaction.atomic
    def add_complex_item(self, user: User, product: Product, quantity: int, specs: Dict) -> CartItem:
        """
        افزودن محصول به سبد خرید.
        نکته: فایل‌ها در این مرحله دریافت نمی‌شوند.
        """
        # 1. استخراج و بررسی دیتای واقعی
        try:
            selected_values = specs.get('option_objs', []) 
        except Exception:
            raise ValueError("اطلاعات ارسالی نامعتبر است.")

        # 2. محاسبه قیمت
        calculator = ProductPriceCalculator(
            product=product,
            quantity=quantity,
            width=specs['width'],
            height=specs['height'],
            selected_values=selected_values,
            has_design=specs.get('has_design', True)
        )
        calc_result = calculator.calculate()
        final_price = Decimal(str(calc_result['final_price']))

        # 3. ساختار JSON
        item_details = {
            'width': specs['width'],
            'height': specs['height'],
            'options': [
                {
                    'id': val.id,
                    'option_name': val.product_option.option.label,
                    'value_label': val.label,
                    'price_impact': float(val.price_impact)
                } for val in selected_values
            ],
            'has_design': specs.get('has_design', True),
            'price_breakdown': calc_result['breakdown']
        }

        # 4. ذخیره در دیتابیس
        cart = self.get_or_create_cart_for_user(user)
        
        cart_item = self._item_repo.create({
            "cart": cart,
            "product": product,
            "quantity": quantity,
            "price": final_price,
            "items": item_details
        })

        return cart_item

    # ===== متد آپدیت اصلاح شده ===== #
    @transaction.atomic
    def update_complex_item(self, user: User, item_id: int, quantity: int, specs: Dict) -> CartItem:
        
        item = self._item_repo.get_item_details(item_id, user)
        if not item:
            raise ItemNotFoundException("آیتم یافت نشد.")

        # 1. استخراج ابعاد جدید
        width, height = self._resolve_dimensions(specs)

        # 2. محاسبه مجدد قیمت
        calculator = ProductPriceCalculator(
            product=item.product,
            quantity=quantity,
            selected_values=specs.get('option_objs', []), # لیست ProductOptionValue
            width=width,
            height=height,
            has_design=specs.get('has_design', True)
        )
        
        price_result = calculator.calculate()
        new_price = Decimal(str(price_result['final_price']))

        # 3. آپدیت JSON
        serializable_specs = {
            'raw_selections': specs.get('raw_selections', {}),
            'items': {
                'width': width,
                'height': height,
                'size_name': specs['size_obj'].size.name if specs.get('size_obj') else 'Custom',
                'options': [
                    {
                        'id': val.id,
                        'name': val.product_option.option.label, 
                        'value': val.label,
                        'price_impact': float(val.price_impact)
                    } 
                    for val in specs.get('option_objs', [])
                ],
                'has_design': specs.get('has_design', True)
            },
            'price_breakdown': price_result['breakdown'] # ذخیره جزئیات
        }

        # 4. ذخیره تغییرات
        updated_item = self._item_repo.update(item, {
            "quantity": quantity,
            "price": new_price,
            "items": serializable_specs
        })
        
        return updated_item
        
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
        
    def clear_cart(self, user: User):
        """خالی کردن کل سبد خرید"""
        cart = self._cart_repo.get_cart_by_user(user)
        if cart:
            self._item_repo.delete_all_items_by_cart(cart)
    
