from typing import Optional, Dict, Tuple
from decimal import Decimal
from django.db import transaction

from .models import Cart, CartItem, Product
from core.models import User
from core.product.services.calculator import ProductPriceCalculator
from .exceptions import ItemNotFoundException

# ========== CART SERVICE ========== #
class CartService:
    """
    سرویس مدیریت سبد خرید (جایگزین CartDomainService)
    """

    # ===== دریافت یا ساخت سبد خرید برای کاربر ===== #
    def get_or_create_cart_for_user(self, user: User) -> Cart:
        """
        سبد خرید یک کاربر را برمی‌گرداند. اگر وجود نداشته باشد، یکی جدید می‌سازد.
        """
        if not user.is_authenticated:
            raise ValueError("کاربر احراز هویت نشده است.")
        
        return Cart.objects.get_or_create_cart(user)
    
    # ===== جستجوی آیتم در سبد خرید ===== #
    def find_item(self, cart: Cart, product: Product, items: Dict) -> Optional[CartItem]:
        return CartItem.objects.find_item_in_cart(cart=cart, product=product, items=items)
    
    def get_item_details(self, cart: Cart):
        return CartItem.objects.get_items_by_cart(cart)
    
    # ===== متد کمکی برای استخراج ابعاد ===== #
    def _resolve_dimensions(self, specs: Dict) -> Tuple[float, float]:
        """
        تشخیص طول و عرض بر اساس اینکه کاربر سایز استاندارد انتخاب کرده یا ابعاد دلخواه.
        """
        size_obj = specs.get('size_obj')
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
        """
        # ===== استخراج ابعاد ===== #
        try:
            selected_values = specs.get('option_objs', []) 
        except Exception:
            raise ValueError("اطلاعات ارسالی نامعتبر است.")

        # ===== محسوب قیمت ===== #
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

        # ===== ساختار JSON ===== #
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

        # ===== ساخت آیتم ===== #
        cart = self.get_or_create_cart_for_user(user)
        
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
            price=final_price,
            items=item_details
        )

        return cart_item

    # ===== متد آپدیت اصلاح شده ===== #
    @transaction.atomic
    def update_complex_item(self, user: User, item_id: int, quantity: int, specs: Dict) -> CartItem:
        
        item = CartItem.objects.get_item_details(item_id, user)
        if not item:
            raise ItemNotFoundException("آیتم یافت نشد.")

        # ===== استخراج ابعاد ===== #
        width, height = self._resolve_dimensions(specs)

        # ===== محاسبه قیمت ===== #
        calculator = ProductPriceCalculator(
            product=item.product,
            quantity=quantity,
            selected_values=specs.get('option_objs', []),
            width=width,
            height=height,
            has_design=specs.get('has_design', True)
        )
        
        price_result = calculator.calculate()
        new_price = Decimal(str(price_result['final_price']))

        # ===== ساختار JSON ===== #
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
            'price_breakdown': price_result['breakdown']
        }

        # ===== ذخیره ===== #
        item.quantity = quantity
        item.price = new_price
        item.items = serializable_specs
        item.save()
        
        return item
        
    # ===== به‌روزرسانی تعداد آیتم در سبد خرید ===== #
    def update_item_quantity(self, item: CartItem, new_quantity: int) -> Optional[CartItem]:
        if new_quantity <= 0:
            item.delete()
            return None
            
        item.quantity = new_quantity
        item.save()
        return item

    # ===== حذف آیتم با چک کردن مالکیت ===== #
    def remove_item(self, user: User, item_id: int):
        """
        حذف با چک کردن مالکیت (Security)
        """
        item = CartItem.objects.get_item_details(item_id, user)
        if not item:
            raise ItemNotFoundException("آیتم یافت نشد یا متعلق به شما نیست.")
        item.delete()
        
    def clear_cart(self, user: User):
        """خالی کردن کل سبد خرید"""
        cart = Cart.objects.get_queryset().get_cart_by_user(user)
        if cart:
            CartItem.objects.delete_all_items_by_cart(cart)

    def get_by_id(self, item_id: int) -> CartItem:
        """
        دریافت مستقیم آیتم سبد خرید (بدون چک کردن مالکیت در لحظه دریافت).
        معمولاً برای استفاده در متدهای داخلی یا ادمین.
        """
        try:
            return CartItem.objects.get(id=item_id)
        except CartItem.DoesNotExist:
            raise ItemNotFoundException("آیتم سبد خرید یافت نشد.")
