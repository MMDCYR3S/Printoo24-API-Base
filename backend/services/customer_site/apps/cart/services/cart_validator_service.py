import logging
from typing import Dict, Any

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError, NotFound

from core.models import (
    Product,
    ProductMaterial,
    ProductSize,
    ProductOption,
    ProductPricingConfig,
)

# ===== تعریف لاگر اختصاصی برای سرویس اعتبارسنجی سبد خرید ===== #
logger = logging.getLogger('shop.services.cart_validator')

class CartDataValidator:
    """
    مسئول اعتبارسنجی داده‌های خام ورودی برای افزودن محصول به سبد خرید.
    
    تغییرات معماری:
    - بررسی تیراژ بر اساس بازه (Min/Max) در ProductPricingConfig.
    - بررسی ابعاد بر اساس محدودیت‌های دستگاه.
    - بررسی همخوانی متریال با محصول.
    """
    
    def validate(self, product_slug: str, selections: Dict[str, Any]) -> Dict[str, Any]:
        """
        اجرای فرآیند اعتبارسنجی داده‌های محصول و انتخاب‌های کاربر.
        """
        logger.info(f"Starting validation for Product Slug: {product_slug}")
        logger.debug(f"Selections received: {selections}")
        
        # ===== 1. بررسی وجود محصول و کانفیگ قیمت ===== #
        try:
            # استفاده از select_related برای پرفورمنس (چون کانفیگ 1:1 است)
            product = Product.objects.select_related('pricing_config').get(slug=product_slug, is_active=True)
        except Product.DoesNotExist:
            logger.warning(f"Product not found or inactive with slug: {product_slug}")
            raise ValidationError("محصول مورد نظر یافت نشد یا غیرفعال است.")

        # دسترسی به کانفیگ قیمت‌گذاری
        config = getattr(product, 'pricing_config', None)
        if not config:
            logger.error(f"Pricing config missing for product: {product.name}")
            raise ValidationError("تنظیمات قیمت‌گذاری برای این محصول یافت نشد.")

        # ===== استخراج داده‌های ورودی ===== #
        # نکته: در معماری جدید، quantity یک عدد است نه ID
        quantity = int(selections.get("quantity", 1))
        # نکته: ID مربوط به ProductMaterial (رابط محصول-جنس) باید ارسال شود
        product_material_id = selections.get("product_material_id") or selections.get("material_id")
        size_id = selections.get("size_id")
        options_ids = selections.get("options_ids", [])
        
        # داده‌های مربوط به ابعاد دلخواه و طراحی
        custom_width = float(selections.get('width', 0))
        custom_height = float(selections.get('height', 0))
        has_design = selections.get('has_design', True)

        try:
            # ===== 2. اعتبارسنجی تیراژ (بر اساس Config) ===== #
            if config.allow_custom_quantity:
                if not (config.min_quantity <= quantity <= config.max_quantity):
                    logger.warning(f"Quantity {quantity} out of range for product {product.name}")
                    raise ValidationError(f"تعداد باید بین {config.min_quantity} و {config.max_quantity} باشد.")
            else:
                # اگر تیراژ دلخواه مجاز نیست، باید چک کنیم که آیا پکیج خاصی مد نظر است 
                # یا صرفاً حداقل را رعایت کرده (بسته به بیزنس شما)
                if quantity < config.min_quantity:
                    raise ValidationError(f"حداقل سفارش برای این محصول {config.min_quantity} عدد است.")

            # ===== 3. اعتبارسنجی متریال (ProductMaterial) ===== #
            if not product_material_id:
                raise ValidationError("انتخاب جنس کاغذ الزامی است.")
            
            # حتماً باید از جدول واسط ProductMaterial چک کنیم تا مطمئن شویم این جنس برای این محصول فعال است
            material_obj = ProductMaterial.objects.get(id=product_material_id, product=product)
            
            # ===== 4. اعتبارسنجی سایز یا ابعاد دلخواه ===== #
            size_obj = None
            custom_dimensions = None

            if size_id:
                # اگر سایز استاندارد انتخاب شده
                size_obj = ProductSize.objects.get(id=size_id, product=product)
            elif config.accepts_custom_dimensions:
                # اگر ابعاد دلخواه وارد شده، باید محدودیت‌های دستگاه چک شود
                if custom_width <= 0 or custom_height <= 0:
                     raise ValidationError("ابعاد وارد شده نامعتبر است.")
                
                # چک کردن Min/Max عرض (مثلاً دستگاه تا عرض 300 سانت می‌زند)
                if config.min_width and custom_width < config.min_width:
                    raise ValidationError(f"حداقل عرض قابل چاپ {config.min_width} سانتیمتر است.")
                if config.max_width and custom_width > config.max_width:
                    raise ValidationError(f"حداکثر عرض قابل چاپ {config.max_width} سانتیمتر است.")
                
                custom_dimensions = {'width': custom_width, 'height': custom_height}
            else:
                raise ValidationError("باید یک سایز استاندارد انتخاب کنید.")

            # ===== 5. اعتبارسنجی آپشن‌های اضافی ===== #
            options_obj = []
            if options_ids:
                # دریافت تمام آپشن‌های معتبر مرتبط با این محصول
                options_obj = list(ProductOption.objects.filter(id__in=options_ids, product=product))
                
                if len(options_obj) != len(options_ids):
                    logger.warning(
                        f"Option mismatch for Product: {product.name}. "
                        f"Requested: {len(options_ids)}, Found: {len(options_obj)}"
                    )
                    raise ValidationError("یک یا چند گزینه انتخاب شده نامعتبر است یا به این محصول تعلق ندارد.")

            # ===== 6. اعتبارسنجی خدمات طراحی ===== #
            if not has_design and not config.design_service_available:
                 logger.warning(f"User requested design but service unavailable for product {product.name}")
                 raise ValidationError("خدمات طراحی برای این محصول ارائه نمی‌شود. لطفاً فایل آپلود کنید.")
            
            logger.debug("All product attributes validated successfully.")

            # ===== بازگرداندن دیکشنری استاندارد شده ===== #
            return {
                "product": product,
                "quantity": quantity,      # int
                "material_obj": material_obj, # ProductMaterial Model Instance
                "size_obj": size_obj,      # ProductSize Model Instance or None
                "options_obj": options_obj, # List[ProductOption]
                "custom_dimensions": custom_dimensions, # Dict or None
                "has_design": has_design,   # bool
            }
            
        except ObjectDoesNotExist as e:
            # هندل کردن کلی خطاهای مربوط به پیدا نشدن متریال/سایز
            logger.error(f"Validation attribute error for Product {product_slug}: {str(e)}")
            raise ValidationError("یکی از ویژگی‌های انتخاب شده (جنس، سایز و...) نامعتبر است.")
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            logger.exception(f"Unexpected validation error for Product {product_slug}")
            raise ValidationError("خطای سیستمی در اعتبارسنجی محصول.")
