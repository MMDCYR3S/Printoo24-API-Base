from typing import List, Optional, Dict, Any

from django.db.models import QuerySet, Max, ProtectedError
from django.db import transaction

from ..exceptions import (
    ProductNotFoundException,
    ProductAlreadyExistsException,
    InvalidProductDataException
)
from .repositories import ProductRepository
from core.models import (
    Product, ProductPricingConfig, ProductQuantity, 
    ProductOption, ProductOptionValue, Option
)

# ======== Product Service ======== #
class ProductDomainService:
    """
    سرویس هسته (Core Service) برای مدیریت منطق بنیادی محصولات.
    این سرویس به عنوان یک رابط تمیز برای ProductRepository عمل می‌کند.
    این لایه هیچ منطق خاصی برای اپلیکیشن‌ها (مانند نحوه نمایش) ندارد.
    """
    
    def __init__(self):
        self._repo = ProductRepository()

    def get_all_active_products(self) -> QuerySet[Product]:
        """
        دریافت لیستی از تمام محصولات فعال.
        مستقیماً متد ریپازیتوری را فراخوانی می‌کند.
        """
        return self._repo.get_all_products()
    
    # ===== متد کمکی برای نمایش جزئیات محصول ===== #
    def _format_product_options(self, product: Product) -> List[Dict[str, Any]]:
        """
        متد کمکی برای تبدیل ساختار آپشن‌های دیتابیس به فرمت استاندارد فرانت‌اند.
        DRY Principle: جلوگیری از تکرار کد در متدهای get_by_id و get_by_slug
        """
        structured_options = []
        for prod_opt in product.options.all():
            option_data = {
                "id": prod_opt.id,
                "name": prod_opt.option.name,
                "label": prod_opt.option.label,
                "is_required": prod_opt.is_required,
                "choices": []
            }
            for choice in prod_opt.choices.all():
                option_data["choices"].append({
                    "id": choice.id,
                    "label": choice.label,
                    "value": choice.value,
                    "price_impact": choice.price_impact,
                    "is_default": choice.is_default,
                })
            structured_options.append(option_data)
        return structured_options
    
    def get_product_detail_by_id(self, product_id: int) -> Dict[str, Any]:
        """
        دریافت جزئیات کامل محصول با استفاده از ID (برای داشبورد).
        خروجی: دیکشنری شامل product و structured_options.
        """
        product = self._repo.get_product_detail_by_id(product_id)
        if not product:
            raise ProductNotFoundException(f"محصول با شناسه {product_id} یافت نشد.")
        
        return {
            "product": product,
            "structured_options": self._format_product_options(product)
        }

    def get_product_detail_by_slug(self, slug: str) -> Optional[Product]:
        """
        مورد استفاده: دریافت جزئیات یک محصول با اسلاگ.
        """
        product = self._repo.get_product_detail_by_slug(slug)
        if not product:
            raise ProductNotFoundException(f"محصول با اسلاگ '{slug}' یافت نشد.")
        
        return {
            "product": product,
            "structured_options": self._format_product_options(product)
        }
            
            
    # ===== Product Shell ===== #
    @transaction.atomic
    def create_product_shell(self, user, data: Dict[str, Any]) -> Product:
        """
        ایجاد محصول اولیه.
        نکته: pricing_config همزمان با محصول ساخته می‌شود (Empty) تا بعدا پر شود.
        """
        # ===== افزودن کاربر ===== #
        data['user'] = user
        # ===== ایجاد محصول ===== #
        product = self._repo.create_product(data)
        # ===== ایجاد تنظیمات قیمت ===== #
        ProductPricingConfig.objects.create(product=product)
        
        return product

    # ===== Product Shell ===== #
    @transaction.atomic
    def update_product_shell(self, pk: int, data: Dict[str, Any]) -> Product:
        product = self._repo.get_by_id(pk)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")
        return self._repo.update_product(product, data)

    # ===== Pricing Config ===== #
    @transaction.atomic
    def update_pricing_config(self, product_id: int, data: Dict[str, Any]):
        product = self._repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")
        config, _ = ProductPricingConfig.objects.get_or_create(product=product)
        for key, value in data.items():
            setattr(config, key, value)
        config.save()
        return config
    
    # ===== وابستگی ها - تیراژ ها ======
    @transaction.atomic
    def sync_quantities(self, product_id: int, user, quantity_ids: List[int]):
        """ همگام‌سازی تیراژها """
        product = self._repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")

        self._repo.clear_quantities(product)

        new_relations = []
        for q_id in quantity_ids:
            new_relations.append(ProductQuantity(
                user=user,
                product=product,
                quantity_id=q_id,
                price=0
            ))
        
        if new_relations:
            ProductQuantity.objects.bulk_create(new_relations)

    # ===== وابستگی ها - ویژگی ها ======
    @transaction.atomic
    def attach_option_from_global(self, product_id: int, option_id: int) -> ProductOption:
        """
        یک ویژگی گلوبال را به محصول وصل می‌کند.
        همزمان مقادیر گلوبال آن ویژگی را هم برای محصول کپی می‌کند (Template Pattern).
        """
        product = self._repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")
            
        # ===== افزودن ویژگی ===== #
        if product.options.filter(option_id=option_id).exists():
            raise InvalidProductDataException("این ویژگی قبلاً به محصول اضافه شده است.")

        # ===== دریافت ویژگی های محصول ===== #
        try:
            global_option = Option.objects.get(id=option_id)
        except Option.DoesNotExist:
            raise InvalidProductDataException("ویژگی گلوبال یافت نشد.")

        # ===== دریافت ترتیب ===== #
        max_order = product.options.aggregate(max_o=Max('order'))['max_o'] or 0
        
        product_option = ProductOption.objects.create(
            product=product,
            option=global_option,
            order=max_order + 1,
        )

        # ===== دریافت مقدارهای ویژگی =====
        global_values = global_option.global_values.all()
        local_values = []
        
        for idx, g_val in enumerate(global_values):
            local_values.append(ProductOptionValue(
                product_option=product_option,
                global_source=g_val,
                label=g_val.label,
                value=g_val.value,
                order=idx,
                price_impact=0
            ))
            
        ProductOptionValue.objects.bulk_create(local_values)
        return product_option
    
    @transaction.atomic
    def update_product_option_config(self, product_id: int, product_option_id: int, data: dict):
        """
        متد اصلی که توسط سرویس اپلیکیشن صدا زده می‌شود.
        هم تنظیمات والد (Option) و هم تنظیمات فرزندان (Values) را آپدیت می‌کند.
        """
        # ===== اعتبارسنجی ===== #
        try:
            prod_opt = ProductOption.objects.get(id=product_option_id, product_id=product_id)
        except ProductOption.DoesNotExist:
            raise InvalidProductDataException(f"این ویژگی متعلق به محصول نیست. ID: {product_option_id}")
        # ===== آپدیت والد ===== #
        if 'is_required' in data:
            prod_opt.is_required = data['is_required']
        prod_opt.save()

        # ===== آپدیت فرزندان ===== #
        if 'values' in data and data['values']:
            valid_ids = {v.id for v in prod_opt.choices.all()}
            # ===== بررسی صحت فرزند بودن ===== #
            for val in data["values"]:
                if val['id'] not in valid_ids:
                    raise InvalidProductDataException("اين مقدار متعلق به ویژگی درخواست شده نیست.")
            # ===== دریافت خطا اگر هر چند ویژگی در حال آپدیت پیش فرض بودند ===== #
            defaults_requested = [v for v in data["values"] if v.get("is_default")]
            if len(defaults_requested) > 1:
                raise InvalidProductDataException("فقط یک مقدار می‌تواند پیش‌فرض باشد.")
            if len(defaults_requested) == 1:
                default_id = defaults_requested[0]['id']
                prod_opt.choices.exclude(id=default_id).update(is_default=False)
            self.update_option_values_pricing(product_id, product_option_id, data['values'])
            
        return prod_opt
    
    @transaction.atomic
    def update_option_values_pricing(self, product_id: int, product_option_id: int, updates: list[dict]):
        """
        بروزرسانی قیمت و تنظیمات مقادیر یک آپشن خاص.
        updates = [{id: 1, price_impact: 5000, is_default: True}, ...]
        """
        # ===== اعتبارسنجی ===== #
        exists = ProductOption.objects.filter(id=product_option_id, product_id=product_id).exists()
        if not exists:
            raise InvalidProductDataException("این آپشن متعلق به محصول درخواست شده نیست.")

        # ===== دریافت مقدارهای فعلی ===== #
        current_values = self._repo.get_product_option_values(product_option_id)
        value_map = {v.id: v for v in current_values}

        # ===== لیست کامل فیلدهایی که باید در دیتابیس آپدیت شوند ===== #
        to_update = []
        fields_to_update = [
            'price_impact', 'is_default', 'order'
        ]

        for item in updates:
            val_id = item.get('id')
            if val_id in value_map:
                obj = value_map[val_id]
                
                # ===== آپدیت فیلدها ===== #
                if 'price_impact' in item:
                    obj.price_impact = item['price_impact']
                if 'is_default' in item:
                    obj.is_default = item['is_default']
                if 'order' in item:
                    obj.order = item['order']

                to_update.append(obj)

        # ===== افزودن پیش‌فرض ===== #
        has_new_default = any(item.get('is_default') for item in updates)
        if has_new_default:
            pass

        # ===== اپدیت ===== #
        if to_update:
            self._repo.bulk_update_option_values(to_update, fields_to_update)
    
    # ===== افزودن ویژگی با قیمت ===== #
    @transaction.atomic
    def attach_option_with_config(self, product_id: int, data: dict) -> ProductOption:
        """
        اتصال ویژگی به محصول + تنظیم قیمت‌ها در همان لحظه.
        """
        product = self._repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")

        option_id = data['option_id']
        
        # ===== اعتبارسنجی ===== #
        if product.options.filter(option_id=option_id).exists():
            raise InvalidProductDataException("این ویژگی قبلاً اضافه شده است.")

        # ===== گلوبال ویژگی ===== #
        try:
            global_option = Option.objects.prefetch_related('global_values').get(id=option_id)
        except Option.DoesNotExist:
            raise InvalidProductDataException("ویژگی گلوبال یافت نشد.")

        # ===== شماره سفارش ===== #
        max_order = product.options.aggregate(max_o=Max('order'))['max_o'] or 0
        
        product_option = ProductOption.objects.create(
            product=product,
            option=global_option,
            order=max_order + 1,
            is_required=data.get('is_required', False),
        )

        # ===== مقادیر (Values) ===== #
        overrides_map = {
            item['global_value_id']: item 
            for item in data.get('values_config', [])
        }

        local_values = []
        global_values = global_option.global_values.all()
        
        for idx, g_val in enumerate(global_values):
            price = 0
            is_default = False
            
            if g_val.id in overrides_map:
                config = overrides_map[g_val.id]
                
                if not config.get('is_active', True):
                    continue
                    
                price = config.get('price_impact', 0)
                is_default = config.get('is_default', False)

            local_values.append(ProductOptionValue(
                product_option=product_option,
                global_source=g_val,
                label=g_val.label,
                value=g_val.value,
                order=idx,
                price_impact=price,
                is_default=is_default
            ))
            
        if local_values:
            ProductOptionValue.objects.bulk_create(local_values)
            
        return product_option

    def delete_product(self, product_id: int):
        """ حذف کامل محصول """
        product = self._repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")
        try:
            product.delete()
        except Exception:
            # ===== حذف با خطا ===== #
            product.is_active = False
            product.save()

    @transaction.atomic
    def detach_option(self, product_id: int, product_option_id: int):
        """ حذف یک ویژگی از محصول """
        # ===== اعتبارسنجی ===== #
        exists = ProductOption.objects.filter(id=product_option_id, product_id=product_id).exists()
        if not exists:
            raise InvalidProductDataException("این ویژگی متعلق به محصول نیست.")
        ProductOption.objects.filter(id=product_option_id).delete()

    # ===== Bulk Operations ===== #
    @transaction.atomic
    def bulk_update_status(self, product_ids: List[int], is_active: bool) -> int:
        """
        تغییر وضعیت گروهی.
        """
        updated_count = Product.objects.filter(id__in=product_ids).update(is_active=is_active)
        return updated_count

    @transaction.atomic
    def bulk_delete_products(self, product_ids: List[int]) -> Dict[str, int]:
        """
        حذف گروهی هوشمند.
        اگر محصول قابل حذف باشد -> Hard Delete
        اگر وابسته باشد (مثلا در سفارشات باشد) -> Soft Delete (is_active=False)
        """
        products = Product.objects.filter(id__in=product_ids)
        deleted_count = 0
        archived_count = 0
        
        for product in products:
            try:
                with transaction.atomic():
                    product.delete()
                    deleted_count += 1
            except (ProtectedError, Exception):
                product.is_active = False
                product.save()
                archived_count += 1
        
        return {
            "deleted_count": deleted_count,
            "archived_count": archived_count,
            "total_processed": len(product_ids)
        }
