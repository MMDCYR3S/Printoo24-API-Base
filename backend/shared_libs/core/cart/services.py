from typing import Optional, Dict, Tuple, Any
from decimal import Decimal

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import (
    User, ProductOption, Cart,
    CartItem, Product, OptionInputType,
    ProductOptionValue, ProductSize,
    ProductQuantity,
)
from core.product.services.calculator import ProductPriceCalculator
from .exceptions import ItemNotFoundException

# ========== CART PROCESSOR ========== #
class CartProcessor:
    """
    کلاس کمکی برای پردازش، اعتبارسنجی و محاسبه قیمت آیتم‌های سبد خرید.
    """
    def __init__(self, product: Product, selections: Dict[str, Any]):
        self.product = product
        self.selections = selections
        self.final_options_data = []
        self.selected_option_values = []
        self.user_raw_inputs = {}
        
    def process(self):
        """
        اجرای تمام مراحل پردازش آپشن‌ها.
        """
        # ===== دریافت ویژگی های مربوط به محصول ===== #
        product_options = self.product.options.all().prefetch_related('choices')
        # ===== انتخاب هایی که فرد انجام داده ===== #
        incoming_options = self.selections.get('options', {})
        # ===== دریافت و اعتبارسنجی انتخابات مشتری ===== #
        for prod_opt in product_options:
            str_opt_id = str(prod_opt.id)
            user_input = incoming_options.get(str_opt_id)
            # ===== چک کردن اجباری بودن ویژگی ===== #
            if prod_opt.is_required and user_input in [None, "", []]:
                raise ValidationError(f"انتخاب ویژگی '{prod_opt.label or prod_opt.name}' الزامی است.")
            # ===== چک کردن فیلدهای غیر اجباری و در صورت نبود، گذ از آن ===== #
            if user_input in [None, "", []]:
                continue
            # ===== اعتبرسنجی و پردازش نوع آپشن و نوع انتخاب کاربر ===== #
            processed_data = self._handle_input_type(prod_opt, user_input)
            # ===== افزودن انتخاب های مشتری به لیست ===== #
            if processed_data:
                self.final_options_data.append(processed_data)
                
    def _handle_input_type(self, prod_opt: ProductOption, user_input: Any) -> Dict:
        """
        تصمیم‌گیری بر اساس Input Type
        """
        itype = prod_opt.input_type
        # ===== نوع انتخاب تکی ===== #
        if itype in [OptionInputType.SELECT, OptionInputType.RADIO]:
            return self._process_single_selection(prod_opt, user_input)
        # ===== نوع انتخاب چندتایی ===== #
        elif itype in [OptionInputType.CHECKBOX, OptionInputType.MULTI_SELECT]:
            return self._process_multi_selection(prod_opt, user_input)
        # ===== نوع انتخاب متنی/عددی ===== #
        elif itype in [OptionInputType.TEXT, OptionInputType.TEXTAREA, OptionInputType.NUMBER]:
            return self._process_raw_input(prod_opt, user_input)

        return {}
    
    def _process_single_selection(self, prod_opt, value_id):
        """ پردازش انتخاب تکی (باید ID معتبر باشد) """
        # ===== دریافت گزینه ها و اعتبارسنجی ===== #
        try:
            choice = prod_opt.choices.get(id=value_id)
        except ProductOptionValue.DoesNotExist:
            raise ValidationError(f"گزینه انتخاب شده برای '{prod_opt.label}' نامعتبر است.")
        # ===== ذخیره ویژگی برای محاسبه قیمت ===== #
        self.selected_option_values.append(choice)
        # ===== بازگردانی یک لیستی از ویژگی ها ===== #
        return {
            "option_id": prod_opt.id,
            "option_label": prod_opt.label or prod_opt.name,
            "type": "selection",
            "value": {
                "id": choice.id,
                "label": choice.label,
                "price": float(choice.price_impact)
            }
        }
        
    def _process_multi_selection(self, prod_opt, value_ids):
        """ پردازش انتخاب چندگانه (لیست ID) """
        # ===== اعتبارسنجی انتخاب ها و در صورت نبود، خطا دادن ===== #
        if not isinstance(value_ids, list):
            raise ValidationError(f"فرمت ورودی برای '{prod_opt.label}' باید لیست باشد.")
        # ===== اعتبارسنجی انتخاب های مشتری ===== #
        choices = prod_opt.choices.filter(id__in=value_ids)
        if len(choices) != len(set(value_ids)):
            raise ValidationError(f"برخی گزینه‌های انتخاب شده برای '{prod_opt.label}' نامعتبر هستند.")
        # ===== افزودن انتخاب های مشتری به لیست ===== #
        selected_items = []
        for choice in choices:
            self.selected_option_values.append(choice)
            selected_items.append({
                "id": choice.id,
                "label": choice.label,
                "price": float(choice.price_impact)
            })
        # ===== بازگردانی لیست ===== #
        return {
            "option_id": prod_opt.id,
            "option_label": prod_opt.label or prod_opt.name,
            "type": "multi_selection",
            "values": selected_items
        }
        
    def _process_raw_input(self, prod_opt, raw_value):
        """ پردازش ورودی متنی یا عددی """
        # ===== ذخیره ورودی کاربر ===== #
        self.user_raw_inputs[str(prod_opt.id)] = str(raw_value)
        # ===== بررسی اینکه آیا نوع آن عدد است یا خیر ===== #
        if prod_opt.input_type == OptionInputType.NUMBER:
            try:
                float(raw_value)
            except Exception as e:
                raise ValidationError(f"مقدار وارد شده برای '{prod_opt.label}' باید عددی باشد.")
        choice = prod_opt.choices.filter(label=raw_value).first()
        self.selected_option_values.append(choice)
        return {
            "option_id": prod_opt.id,
            "option_label": prod_opt.label or prod_opt.name,
            "type": "raw",
            "value": str(raw_value),
            "price": float(prod_opt.price_impact)
        }


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
    
    def get_cart_item_for_user(self, user: User, item_id: int) -> CartItem:
        """
        دریافت یک آیتم خاص برای کاربر (جهت نمایش جزئیات).
        """
        # استفاده از منیجر برای دریافت آیتم با چک کردن مالکیت
        item = CartItem.objects.get_item_by_id(item_id, user)
        
        if not item:
            raise ItemNotFoundException("آیتم سبد خرید یافت نشد یا متعلق به شما نیست.")
            
        return item
    
    # ===== متد کمکی برای استخراج ابعاد ===== #
    def _resolve_dimensions(self, product: Product, selections: Dict) -> Tuple[float, float]:
        """
        تشخیص طول و عرض:
        1. اگر size_id انتخاب شده باشد -> از دیتابیس میخواند.
        2. اگر ابعاد دلخواه (custom) باشد -> از ورودی میخواند.
        """
        size_id = selections.get('size_id')
        custom_width = selections.get('width')
        custom_height = selections.get('height')
        # ===== اگر سایز انتخاب شد ===== #
        if size_id:
            try:
                ps = ProductSize.objects.get(product=product, id=size_id)
                return float(ps.size.width), float(ps.size.height)
            except ProductSize.DoesNotExist:
                raise ValidationError(_("سایز انتخاب شده نامعتبر است."))
        if custom_width and custom_height:
            return float(custom_width), float(custom_height)
        return 0.0, 0.0

    def _handle_quantity_logic(self, product: Product, quantity_input: int, selections: Dict) -> Tuple[int, Decimal]:
        """
        مدیریت پیچیده تیراژ:
        خروجی: (تعداد نهایی برای ذخیره در آیتم، قیمت پایه واحد)
        """
        # ===== دریافت تیراژ ===== #
        final_quantity = quantity_input
        base_unit_price = Decimal(0)
        # ===== اگر محصول به صورت تیراژی بود ===== #
        if product.has_quantity:
            qty_id = selections.get('quantity_id')
            if not qty_id:
                raise ValidationError(_("برای این محصول انتخاب 'تیراژ' (بسته) الزامی است."))

            try:
                # ===== دریافت تیراژ مربوط به محصول براساس انتخاب کاربر ===== #
                pq = ProductQuantity.objects.select_related('quantity').get(product=product, id=qty_id)
                final_quantity = quantity_input if quantity_input > 0 else 1
                base_unit_price = Decimal(pq.price)
            # ===== خطا در صورت نبود تیراژ ===== #
            except ProductQuantity.DoesNotExist:
                raise ValidationError(_("تیراژ انتخابی نامعتبر است."))
        else:
            # ===== اگر محصول به صورت تیراژی نبود ===== #
            config = getattr(product, 'pricing_config', None)
            # ===== اگر پیکربندی قیمت وجود داشت ===== #
            if config:
                if not config.allow_custom_quantity:
                    raise ValidationError(_("نمی توانید به صورت دلخواه این تیراژ را انتخاب کنید."))
                if quantity_input < config.min_quantity:
                    raise ValidationError(f"حداقل تعداد سفارش {config.min_quantity} عدد است.")
                if quantity_input > config.max_quantity:
                    raise ValidationError(f"حداکثر تعداد سفارش {config.max_quantity} عدد است.")
            final_quantity = quantity_input
            base_unit_price = product.price
            
        return final_quantity, base_unit_price

    # ===== متد افزودن به سبد خرید. ===== #
    @transaction.atomic
    def add_item_to_cart(self, user: User, product_id: int, quantity_input: int, selections: Dict[str, Any]):
        """
        افزودن محصول به سبد خرید.
        """
        # ===== دریافت محصول ===== #
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise ValidationError(_("محصول یافت نشد یا غیرفعال است."))
        # ===== استفاده از پردازشگر ویژگی ها ===== #
        processor = CartProcessor(product, selections)
        processor.process()
        # ===== دریافت تیراژ ===== #
        final_quantity, base_unit_price = self._handle_quantity_logic(product, quantity_input, selections)
        # ===== دریافت ابعاد ===== #
        width, height = self._resolve_dimensions(product, selections)
        # ===== محاسبه قیمت ===== #
        calculator = ProductPriceCalculator(
            product=product,
            quantity=final_quantity,
            width=width,
            height=height,
            selected_values=processor.selected_option_values,
            user_input_data=processor.user_raw_inputs,
            selected_size_id=selections.get('size_id'),
            has_design=selections.get('has_design', True)
        )
        calc_result = calculator.calculate()
        final_price = Decimal(str(calc_result['final_price']))
        # ===== ایجاد ساختار نهایی سبد خرید ===== #
        cart_item_data = {
            "options": processor.final_options_data,
            "meta": {
                "width": width,
                "height": height,
                "size_id": selections.get('size_id'),
                "quantity_id": selections.get('quantity_id'),
                "has_design": selections.get('has_design', True),
                "price_breakdown": calc_result['breakdown']
            }
        }
        
        # ===== انتخاب نوع سایز محصول ===== #
        if 'size_id' in selections:
            cart_item_data['size_id'] = selections['size_id'] 
        # ===== دریافت یا ایجاد سبد خرید برای کاربر ===== #
        cart = Cart.objects.get_or_create_cart(user)
        # ===== چک کردن تکراری بودن نوع سفارش و آیتم ها ===== #
        existing_item = CartItem.objects.find_item_in_cart(cart, product, cart_item_data)
        # ===== آپدیت سفارش تکراری ===== #
        if existing_item:
            existing_item.quantity += final_quantity
            existing_item.price = final_price 
            existing_item.save()
            return existing_item
        # ===== در صورت نبود، ایجاد آن در سبد خرید ===== #
        else:
            new_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=final_quantity,
                price=final_price,
                items=cart_item_data
            )
            return new_item
        
        
    # ===== متد آپدیت اصلاح شده ===== #
    @transaction.atomic
    def update_cart_item(self, user: User, item_id: int, quantity_input: int, selections: Dict[str, Any]) -> CartItem:
        """
        آپدیت کامل آیتم (تعداد + آپشن‌ها).
        اگر آپشن‌ها تغییر کنند، ممکن است آیتم با آیتم دیگری ادغام شود.
        """
        # ===== دریافت آیتم ===== #
        current_item = CartItem.objects.get_item_details(item_id, user)
        if not current_item:
            raise ItemNotFoundException("آیتم سبد خرید یافت نشد.")
        # ===== دریافت محصول ===== #
        product = current_item.product
        # ===== دریافت تیراژ فعلی ===== #
        final_quantity, base_unit_price = self._handle_quantity_logic(product, quantity_input, selections)
        # ===== استفاده از پردازشگر ویژگی ها ===== #
        processor = CartProcessor(product, selections)
        processor.process()
        # ===== دریافت ابعاد ===== #
        width, height = self._resolve_dimensions(product, selections)
        # ===== محاسبه قیمت ===== #
        calculator = ProductPriceCalculator(
            product=product,
            quantity=final_quantity,
            width=width,
            height=height,
            selected_values=processor.selected_option_values,
            user_input_data=processor.user_raw_inputs,
            selected_size_id=selections.get('size_id'),
            has_design=selections.get('has_design', True)
        )
        calc_result = calculator.calculate()
        new_total_price = Decimal(str(calc_result['final_price']))
        # ===== آپدیت آیتم ===== #
        new_cart_item_data = {
            "options": processor.final_options_data,
            "meta": {
                "width": width,
                "height": height,
                "size_id": selections.get('size_id'),
                "quantity_id": selections.get('quantity_id'),
                "has_design": selections.get('has_design', True),
                "price_breakdown": calc_result['breakdown']
            }
        }
        # ===== دریافت سبد خرید ===== #
        cart = current_item.cart
        # ===== بررسی اینکه آیا آیتم تکراری است ===== #
        duplicate_item = CartItem.objects.filter(
            cart=cart, 
            product=product, 
            items=new_cart_item_data
        ).exclude(id=current_item.id).first()
        if duplicate_item:
            duplicate_item.quantity += final_quantity
            duplicate_item.price += new_total_price
            duplicate_item.save()
            current_item.delete()
            return duplicate_item
        else:
            current_item.quantity = final_quantity
            current_item.price = new_total_price
            current_item.items = new_cart_item_data
            current_item.save()
            return current_item
        
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
