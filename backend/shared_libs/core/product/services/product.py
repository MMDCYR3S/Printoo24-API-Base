from typing import List, Optional, Dict, Any
from django.db.models import Max, ProtectedError
from django.db import transaction

from ..exceptions import (
    ProductNotFoundException,
    InvalidProductDataException
)
from ..models import (
    Product, ProductPricingConfig, ProductQuantity, 
    ProductOption, ProductOptionValue, Option
)

class ProductService:
    """
    سرویس مدیریت منطق محصولات (جایگزین ProductDomainService).
    """

    # ===== Read Operations ===== #
    def get_all_active_products(self):
        return Product.objects.get_all_active_products()
    
    def _format_product_options(self, product: Product) -> List[Dict[str, Any]]:
        """
        متد کمکی برای تبدیل ساختار آپشن‌های دیتابیس به فرمت استاندارد فرانت‌اند.
        """
        structured_options = []
        # ===== تبدیل ساختار آپشن‌ها ===== #
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
        try:
            product = Product.objects.get_product_detail_by_id(product_id)
        except Product.DoesNotExist:
            raise ProductNotFoundException(f"محصول با شناسه {product_id} یافت نشد.")
        
        return {
            "product": product,
            "structured_options": self._format_product_options(product)
        }

    def get_product_detail_by_slug(self, slug: str) -> Optional[Product]:
        product = Product.objects.get_product_detail_by_slug(slug)
        if not product:
            raise ProductNotFoundException(f"محصول با اسلاگ '{slug}' یافت نشد.")
        
        return {
            "product": product,
            "structured_options": self._format_product_options(product)
        }

    # ===== Write Operations (Shell) ===== #
    @transaction.atomic
    def create_product_shell(self, user, data: Dict[str, Any]) -> Product:
        """
        ایجاد محصول اولیه.
        """
        data['user'] = user
        product = Product.objects.create(**data)
        
        # ===== ایجاد پیکربندی قیمت ===== #
        ProductPricingConfig.objects.create(product=product)
        
        return product

    @transaction.atomic
    def update_product_shell(self, pk: int, data: Dict[str, Any]) -> Product:
        product = Product.objects.get_by_id(pk)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")
        
        # جایگزین: self._repo.update_product
        for key, value in data.items():
            setattr(product, key, value)
        product.save()
        return product

    # ===== Pricing Config ===== #
    @transaction.atomic
    def update_pricing_config(self, product_id: int, data: Dict[str, Any]):
        product = Product.objects.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")
            
        config, _ = ProductPricingConfig.objects.get_or_create(product=product)
        for key, value in data.items():
            setattr(config, key, value)
        config.save()
        return config

    # ===== Quantity Logic ===== #
    @transaction.atomic
    def sync_quantities(self, product_id: int, user, quantity_ids: List[int]):
        """ همگام‌سازی تیراژها """
        product = Product.objects.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")

        # ===== حذف تیراژهای قبلی ===== #
        ProductQuantity.objects.filter(product=product).delete()

        # ===== ایجاد تیراژهای جدید ===== #
        new_relations = [
            ProductQuantity(user=user, product=product, quantity_id=qid, price=0)
            for qid in quantity_ids
        ]
        
        if new_relations:
            ProductQuantity.objects.bulk_create(new_relations)

    # ===== Options Logic ===== #
    @transaction.atomic
    def attach_option_from_global(self, product_id: int, option_id: int) -> ProductOption:
        product = Product.objects.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")
            
        if product.options.filter(option_id=option_id).exists():
            raise InvalidProductDataException("این ویژگی قبلاً به محصول اضافه شده است.")

        try:
            global_option = Option.objects.get(id=option_id)
        except Option.DoesNotExist:
            raise InvalidProductDataException("ویژگی گلوبال یافت نشد.")

        # دریافت Max Order
        max_order = product.options.aggregate(max_o=Max('order'))['max_o'] or 0
        
        product_option = ProductOption.objects.create(
            product=product,
            option=global_option,
            order=max_order + 1,
        )

        # کپی ولیوها (Template Pattern)
        global_values = global_option.global_values.all()
        local_values = [
            ProductOptionValue(
                product_option=product_option,
                global_source=g_val,
                label=g_val.label,
                value=g_val.value,
                order=idx,
                price_impact=0
            )
            for idx, g_val in enumerate(global_values)
        ]
            
        ProductOptionValue.objects.bulk_create(local_values)
        return product_option

    @transaction.atomic
    def update_product_option_config(self, product_id: int, product_option_id: int, data: dict):
        try:
            prod_opt = ProductOption.objects.get(id=product_option_id, product_id=product_id)
        except ProductOption.DoesNotExist:
            raise InvalidProductDataException(f"این ویژگی متعلق به محصول نیست. ID: {product_option_id}")
        
        if 'is_required' in data:
            prod_opt.is_required = data['is_required']
        prod_opt.save()

        if 'values' in data and data['values']:
            valid_ids = {v.id for v in prod_opt.choices.all()}
            for val in data["values"]:
                if val['id'] not in valid_ids:
                    raise InvalidProductDataException("اين مقدار متعلق به ویژگی درخواست شده نیست.")
            
            defaults_requested = [v for v in data["values"] if v.get("is_default")]
            if len(defaults_requested) > 1:
                raise InvalidProductDataException("فقط یک مقدار می‌تواند پیش‌فرض باشد.")
            if len(defaults_requested) == 1:
                default_id = defaults_requested[0]['id']
                prod_opt.choices.exclude(id=default_id).update(is_default=False)
            
            self._update_option_values_pricing_logic(product_id, product_option_id, data['values'])
            
        return prod_opt

    @transaction.atomic
    def _update_option_values_pricing_logic(self, product_id: int, product_option_id: int, updates: list[dict]):
        """
        لاجیک آپدیت ولیوها (قبلاً در ریپازیتوری بود، الان پرایوت متد سرویس شده)
        """
        exists = ProductOption.objects.filter(id=product_option_id, product_id=product_id).exists()
        if not exists:
            raise InvalidProductDataException("این آپشن متعلق به محصول درخواست شده نیست.")

        current_values = ProductOptionValue.objects.filter(product_option_id=product_option_id)
        value_map = {v.id: v for v in current_values}

        to_update = []
        fields_to_update = ['price_impact', 'is_default', 'order']

        for item in updates:
            val_id = item.get('id')
            if val_id in value_map:
                obj = value_map[val_id]
                if 'price_impact' in item:
                    obj.price_impact = item['price_impact']
                if 'is_default' in item:
                    obj.is_default = item['is_default']
                if 'order' in item:
                    obj.order = item['order']
                to_update.append(obj)

        if to_update:
            ProductOptionValue.objects.bulk_update(to_update, fields_to_update)

    @transaction.atomic
    def attach_option_with_config(self, product_id: int, data: dict) -> ProductOption:
        product = Product.objects.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")

        option_id = data['option_id']
        if product.options.filter(option_id=option_id).exists():
            raise InvalidProductDataException("این ویژگی قبلاً اضافه شده است.")

        try:
            global_option = Option.objects.prefetch_related('global_values').get(id=option_id)
        except Option.DoesNotExist:
            raise InvalidProductDataException("ویژگی گلوبال یافت نشد.")

        max_order = product.options.aggregate(max_o=Max('order'))['max_o'] or 0
        
        product_option = ProductOption.objects.create(
            product=product,
            option=global_option,
            order=max_order + 1,
            is_required=data.get('is_required', False),
        )

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
        product = Product.objects.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")
        try:
            product.delete()
        except Exception:
            product.is_active = False
            product.save()

    @transaction.atomic
    def detach_option(self, product_id: int, product_option_id: int):
        exists = ProductOption.objects.filter(id=product_option_id, product_id=product_id).exists()
        if not exists:
            raise InvalidProductDataException("این ویژگی متعلق به محصول نیست.")
        ProductOption.objects.filter(id=product_option_id).delete()

    # ===== Bulk Operations ===== #
    @transaction.atomic
    def bulk_update_status(self, product_ids: List[int], is_active: bool) -> int:
        return Product.objects.filter(id__in=product_ids).update(is_active=is_active)

    @transaction.atomic
    def bulk_delete_products(self, product_ids: List[int]) -> Dict[str, int]:
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
