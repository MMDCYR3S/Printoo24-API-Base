from typing import Optional, Dict, Tuple

from decimal import Decimal
from django.db import transaction

from core.models import (
    Cart,
    CartItem,
    CartItemUpload,
    Product,
    ProductFileUploadRequirement,
    ProductSize,
    User,
)
from core.domain.product import ProductPriceCalculator
from core.domain.cart.exceptions import (
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

    # ===== افزودن آیتم پیچیده به سبد خرید ===== #
    @transaction.atomic
    def add_complex_item(self, user: User, product: Product, quantity: int, 
                          specs: Dict, uploaded_files_map: Dict[int, str]) -> CartItem:
        """
        Args:
            specs: شامل material_obj (ProductMaterial), size_obj, option_objs, custom_dimensions, has_design
        """
        if quantity <= 0:
            raise InvalidQuantityException("تعداد باید بیشتر از صفر باشد.")
        
        # 1. استخراج ابعاد برای محاسبه مساحت
        width, height = self._resolve_dimensions(specs)

        # 2. فراخوانی محاسبه‌گر جدید
        calculator = ProductPriceCalculator(
            product=product,
            product_material=specs['material_obj'], # آبجکت ProductMaterial
            quantity=quantity,
            options=specs.get('option_objs', []),
            width=width,
            height=height,
            has_design=specs.get('has_design', True) # پیش‌فرض true یعنی فایل دارد
        )
        
        price_result = calculator.calculate()
        final_price = Decimal(str(price_result['final_price']))

        # 3. آماده‌سازی داده‌های JSON برای ذخیره در دیتابیس
        # ما باید نام‌ها را ذخیره کنیم تا اگر بعداً قیمت‌ها عوض شد، تاریخچه سفارش تغییر نکند
        serializable_specs = {
            'raw_selections': specs.get('raw_selections', {}), # ID های خام ارسالی از فرانت
            'details': {
                'width': width,
                'height': height,
                'material_name': specs['material_obj'].material.name,
                'size_name': specs['size_obj'].size.name if specs.get('size_obj') else 'Custom',
                'options': [
                    {'name': opt.option.name, 'price_impact': float(opt.price_impact)} 
                    for opt in specs.get('option_objs', [])
                ],
                'has_design': specs.get('has_design', True)
            },
            'price_breakdown': price_result # ذخیره جزئیات محاسبات برای شفافیت
        }

        cart = self._cart_repo.get_or_create_cart(user)
        
        # 4. ذخیره آیتم
        cart_item = self._item_repo.create({
            "cart": cart,
            "product": product,
            "quantity": quantity,
            "price": final_price,
            "items": serializable_specs # فیلد JSONField مدل CartItem
        })

        # 5. اتصال فایل‌های آپلود شده
        for req_id, file_path in uploaded_files_map.items():
            requirement = ProductFileUploadRequirement.objects.get(id=req_id)
            CartItemUpload.objects.create(
                cart_item=cart_item,
                requirement=requirement,
                file=file_path
            )

        return cart_item
    
    # ===== افزودن فایل به یک آیتم =====
    @transaction.atomic
    def update_complex_item(self, user: User, item_id: int, 
                            quantity: int, specs: Dict) -> CartItem:
        
        item = self._item_repo.get_item_details(item_id, user)
        if not item:
            raise ItemNotFoundException("آیتم یافت نشد.")

        # 1. استخراج ابعاد (ممکن است کاربر سایز را تغییر داده باشد)
        width, height = self._resolve_dimensions(specs)

        # 2. محاسبه مجدد قیمت
        calculator = ProductPriceCalculator(
            product=item.product,
            product_material=specs['material_obj'],
            quantity=quantity,
            options=specs.get('option_objs', []),
            width=width,
            height=height,
            has_design=specs.get('has_design', True)
        )
        
        price_result = calculator.calculate()
        new_price = Decimal(str(price_result['final_price']))

        # 3. آپدیت JSON
        serializable_specs = {
            'raw_selections': specs.get('raw_selections', {}),
            'details': {
                'width': width,
                'height': height,
                'material_name': specs['material_obj'].material.name,
                'size_name': specs['size_obj'].size.name if specs.get('size_obj') else 'Custom',
                'options': [
                    {'name': opt.option.name, 'price_impact': float(opt.price_impact)} 
                    for opt in specs.get('option_objs', [])
                ],
                'has_design': specs.get('has_design', True)
            },
            'price_breakdown': price_result
        }

        updated_item = self._item_repo.update(item, {
            "quantity": quantity,
            "price": new_price,
            "items": serializable_specs
        })
        
        return updated_item
        
        # ===== اپدیت قیمت ===== #
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
    
