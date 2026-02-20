from typing import List, Optional, Dict, Any
from django.db.models import Max, ProtectedError
from django.db import transaction
from django.utils import timezone

from ..exceptions import (
    ProductNotFoundException,
    InvalidProductDataException
)
from ..models import (
    Product, ProductPricingConfig, ProductQuantity, 
    ProductOption, ProductOptionValue, Option, ProductSize,
    ProductQuantity, Quantity, Size, ProductCategory,
    OptionValueQuantityPrice, ProductOptionCondition
)

class ProductService:
    """
    سرویس مدیریت منطق محصولات (جایگزین ProductDomainService).
    """

    # ===== Read Operations ===== #
    def get_all_active_products(self):
        return Product.objects.get_all_active_products()
    
    def get_all_products(self):
        return Product.objects.get_all()
    
    def _format_product_options(self, product: Product) -> List[Dict[str, Any]]:
        """
        متد کمکی برای تبدیل ساختار آپشن‌های دیتابیس به فرمت استاندارد فرانت‌اند.
        """
        structured_options = []
        # ===== تبدیل ساختار آپشن‌ها ===== #
        for prod_opt in product.options.all():
            if prod_opt.option:
                     choice_input_type = prod_opt.option.input_type
            option_data = {
                "id": prod_opt.id,
                "name": prod_opt.option.name,
                "label": prod_opt.option.label,
                "input_type": choice_input_type,
                "is_required": prod_opt.is_required,
                "choices": []
            }
            
            for choice in prod_opt.choices.all():
                
                option_data["choices"].append({
                    "id": choice.id,
                    "label": choice.label,
                    "value": choice.value,
                    "input_type": choice_input_type,
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
            "product": product
            # "structured_options": self._format_product_options(product)
        }

    @transaction.atomic
    def sync_sizes(self, product_id: int, user, size_configs: List[Dict]):
        """
        همگام‌سازی سایزهای محصول.
        ورودی: لیستی از دیکشنری‌ها شامل id و price_impact
        """

        product = Product.objects.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")

        # ===== اعتبارسنجی وجود سایزها ===== #
        size_ids = [item['id'] for item in size_configs]
        valid_sizes_count = Size.objects.filter(id__in=size_ids).count()
        if valid_sizes_count != len(set(size_ids)):
             raise InvalidProductDataException("برخی از شناسه های سایز نامعتبر هستند.")

        # ===== حذف سایزهای قبلی (Full Sync Strategy) ===== #
        ProductSize.objects.filter(product=product).delete()

        # ===== ایجاد سایزهای جدید ===== #
        new_relations = [
            ProductSize(
                user=user, 
                product=product, 
                size_id=item['id'], 
                price_impact=item.get('price_impact', 0),
                guide_text=item.get('guide_text', ''),
                guide_type=item.get('guide_type', 'info')
            )
            for item in size_configs
        ]
        
        if new_relations:
            ProductSize.objects.bulk_create(new_relations)

    def get_products_by_category_ids(self, category_ids: List[int]):
        """
        دریافت محصولات بر اساس لیست دسته‌بندی‌ها (برای لندینگ و فیلتر).
        """
        return Product.objects.get_products_by_category_ids(category_ids)

    def get_product_detail_by_slug(self, slug: str) -> Optional[Product]:
        product = Product.objects.get_product_detail_by_slug(slug)
        if not product:
            raise ProductNotFoundException(f"محصول با اسلاگ '{slug}' یافت نشد.")
        
        return {
            "product": product,
            # "structured_options": self._format_product_options(product)
        }

    # ===== Write Operations (Shell) ===== #
    @transaction.atomic
    def create_product_shell(self, user, data: Dict[str, Any]) -> Product:
        """
        ایجاد محصول اولیه.
        """
        category_id = data.pop('category_id', None)
        category_ids = data.pop('category_ids', [])
        
        if category_id:
            category_ids.append(category_id)
        
        data['user'] = user
        product = Product.objects.create(**data)
        
        if category_ids:
            self.assign_categories(product, category_ids)
        
        # ===== ایجاد پیکربندی قیمت ===== #
        ProductPricingConfig.objects.create(product=product)
        
        return product

    @transaction.atomic
    def update_product_shell(self, pk: int, data: Dict[str, Any]) -> Product:
        product = Product.objects.get_by_id(pk)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")
        
        category_id = data.pop('category_id', None)
        category_ids = data.pop('category_ids', None)
        
        # جایگزین: self._repo.update_product
        for key, value in data.items():
            setattr(product, key, value)
        product.save()
        
        if category_ids is not None:
             self.assign_categories(product, category_ids)
        elif category_id is not None:
             self.assign_categories(product, [category_id])
        
        return product

    # ===== Assign Categories ===== #
    def assign_categories(self, product: Product, category_ids: List[int]):
        """
        متد کمکی برای مدیریت اتصال دسته‌بندی‌ها.
        سیگنال‌های تعریف شده در مدل، خودکار کد محصول را آپدیت می‌کنند.
        """
        if not category_ids:
            product.categories.clear()
            return
        
        # ===== اعتبارسنجی وجود دسته‌بندی‌ها ===== #
        selected_categories = ProductCategory.objects.filter(id__in=category_ids)
        
        if not selected_categories.exists():
            return
        
        # ===== فقط دسته بندی فرزند سطح پایین انتخاب خواهد شد. ===== #
        target_category = sorted(selected_categories, key=lambda x: x.level, reverse=True)[0]
        
        product.categories.set([target_category.id])

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

    # ===== Quantity Logic (Refactored) ===== #
    @transaction.atomic
    def sync_quantities(self, product_id: int, user, quantity_configs: List[Dict]):
        """ 
        همگام‌سازی تیراژها با قیمت اختصاصی.
        ورودی: لیستی از دیکشنری‌ها شامل {id, price}
        """
        # ===== دریافت محصول ===== #
        product = Product.objects.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")

        # ===== اعتبارسنجی وجود تیراژها ===== #
        quantity_ids = [item['id'] for item in quantity_configs]
        valid_count = Quantity.objects.filter(id__in=quantity_ids).count()
        
        if valid_count != len(set(quantity_ids)):
             raise InvalidProductDataException("برخی از شناسه‌های تیراژ نامعتبر هستند.")

        # ===== حذف تیراژهای قبلی ===== #
        ProductQuantity.objects.filter(product=product).delete()

        # ===== ایجاد تیراژهای جدید با قیمت ===== #
        new_relations = [
            ProductQuantity(
                user=user, 
                product=product, 
                quantity_id=item['id'], 
                price=item.get('price', 0),
                guide_text=item.get('guide_text', ''),
                guide_type=item.get('guide_type', 'info')
            )
            for item in quantity_configs
        ]
        
        if new_relations:
            ProductQuantity.objects.bulk_create(new_relations)

    # ===== Options Logic ===== #
    @transaction.atomic
    def attach_option_with_config(self, product_id: int, data: dict):
        """
        اتصال یک ویژگی (از بانک یا کاستوم) به محصول 
        + ذخیره ماتریس قیمت تیراژ 
        + بازگرداندن دیکشنری ref_id ها برای ساخت شرط‌ها در فاز دوم.
        """
        from ..models import OptionValueQuantityPrice
        
        product = Product.objects.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")

        option_id = data.get('option_id')
        global_option = None
        
        # ===== حالت ۱: اتصال به بانک (Linked) ===== #
        if option_id:
            if product.options.filter(option_id=option_id).exists():
                raise InvalidProductDataException("این ویژگی قبلاً اضافه شده است.")
            try:
                global_option = Option.objects.prefetch_related('global_values').get(id=option_id)
            except Option.DoesNotExist:
                raise InvalidProductDataException("ویژگی گلوبال یافت نشد.")

        max_order = product.options.aggregate(max_o=Max('order'))['max_o'] or 0
        
        # ===== فیلدهای ساخت یک ویژگی ===== #
        create_kwargs = {
            "product": product,
            "option": global_option,
            "order": max_order + 1,
            "is_required": data.get('is_required', False),
            "guide_text": data.get('guide_text', ''),
            "guide_type": data.get('guide_type', 'info')
        }
        
        # ===== حالت ۲: اگر ویژگی کاملا سفارشی و کاستوم هست ===== #
        if not global_option:
            create_kwargs.update({
                "name": data.get('name', f'custom_option_{timezone.now().timestamp()}'),
                "label": data.get('label', 'Custom Option'),
                "input_type": data.get('input_type', 'select')
            })
            
        product_option = ProductOption.objects.create(**create_kwargs)
        
        # ===== پردازش مقادیر فیلدها ===== #
        input_configs = data.get('values_config', [])

        # نگاشت برای مقادیری که از بانک آمده‌اند
        linked_configs_map = {
            item.get('global_value_id'): item 
            for item in input_configs if item.get('global_value_id')
        }
        
        # جداسازی مقادیر کاملاً کاستوم
        custom_configs = [item for item in input_configs if not item.get('global_value_id')]
        
        # کش کردن تیراژهای محصول برای استفاده در ماتریس
        product_quantities = {pq.quantity_id: pq for pq in product.product_quantity.all()}
        
        current_display_order = 0
        
        # خروجی‌ها برای مرحله دوم (Pass 2)
        created_values_with_refs = {}
        matrix_to_create = []
        
        # ===== ۱. ساخت مقادیر برگرفته از بانک ===== #
        if global_option:
            global_values = global_option.global_values.all()
            for g_val in global_values:
                config = linked_configs_map.get(g_val.id, {})
                should_create = config.get('is_active', True)
            
                if should_create:
                    # ساخت و ذخیره تکی مقدار (برای دریافت شناسه واقعی در دیتابیس)
                    val_obj = ProductOptionValue(
                        product_option=product_option,
                        global_source=g_val,
                        label=config.get('label', g_val.label),  
                        value=config.get('value', g_val.value),
                        order=current_display_order,
                        price_impact=config.get('price_impact', 0),
                        is_default=config.get('is_default', False),
                        guide_text=config.get('guide_text', g_val.guide_text),
                        guide_type=config.get('guide_type', g_val.guide_type)
                    )
                    val_obj.save() 
                    current_display_order += 1
                    
                    # ذخیره در دیکشنری رف‌نس‌ها اگر فرانت‌اند ref_id داده باشد
                    ref_id = config.get('ref_id')
                    if ref_id:
                        created_values_with_refs[ref_id] = val_obj

                    # آماده‌سازی ماتریس قیمت تیراژ برای این مقدار
                    for qp in config.get('quantity_prices', []):
                        pq = product_quantities.get(qp['quantity_id'])
                        if pq:
                            matrix_to_create.append(OptionValueQuantityPrice(
                                option_value=val_obj,
                                product_quantity=pq,
                                price=qp.get('price', 0)
                            ))

        # ===== ۲. ساخت مقادیر کاملاً کاستوم ===== #
        for custom_item in custom_configs:
            if not custom_item.get('label'):
                raise InvalidProductDataException("برای مقادیر سفارشی (Custom)، وارد کردن عنوان (Label) الزامی است.")

            # ساخت و ذخیره تکی مقدار
            val_obj = ProductOptionValue(
                product_option=product_option,
                global_source=None,
                label=custom_item['label'],
                value=custom_item.get('value', custom_item['label']),
                order=current_display_order,
                price_impact=custom_item.get('price_impact', 0),
                is_default=custom_item.get('is_default', False),
                guide_text=custom_item.get('guide_text', ''),
                guide_type=custom_item.get('guide_type', 'info')
            )
            val_obj.save()
            current_display_order += 1
            
            # ذخیره در دیکشنری رف‌نس‌ها اگر فرانت‌اند ref_id داده باشد
            ref_id = custom_item.get('ref_id')
            if ref_id:
                created_values_with_refs[ref_id] = val_obj
            
            # آماده‌سازی ماتریس قیمت تیراژ برای این مقدار
            for qp in custom_item.get('quantity_prices', []):
                pq = product_quantities.get(qp['quantity_id'])
                if pq:
                    matrix_to_create.append(OptionValueQuantityPrice(
                        option_value=val_obj,
                        product_quantity=pq,
                        price=qp.get('price', 0)
                    ))
                    
        # ===== ذخیره دسته‌جمعی ماتریس (Performance Boost) ===== #
        if matrix_to_create:
            OptionValueQuantityPrice.objects.bulk_create(matrix_to_create)
            
        return product_option, created_values_with_refs

    @transaction.atomic
    def create_bulk_conditions(self, ref_map: dict, pending_conditions: list):
        """
        ساخت دسته‌جمعی شرط‌ها بر اساس نگاشت شناسه‌های موقت (ref_id) 
        به آبجکت‌های واقعی دیتابیس.
        """
        from ..models import ProductOptionCondition
        conditions_to_create = []
        
        for item in pending_conditions:
            target_obj = ref_map.get(item['target_ref'])
            if not target_obj:
                continue
                
            for cond in item['conditions']:
                req_ref_id = cond.get('required_ref_id')
                req_val_id = cond.get('required_value_id')
                
                # پیدا کردن پیش‌نیاز (یا از طریق آیدی واقعی دیتابیس یا از طریق شناسه موقت)
                req_obj = None
                if req_ref_id:
                    req_obj = ref_map.get(req_ref_id)
                elif req_val_id:
                    req_obj = ProductOptionValue.objects.filter(id=req_val_id).first()
                
                # جلوگیری از ساخت شرط به خودش یا هم‌گروه خودش
                if req_obj and req_obj.product_option_id != target_obj.product_option_id:
                    conditions_to_create.append(ProductOptionCondition(
                        target_value=target_obj,
                        required_value=req_obj,
                        action=cond.get('action', 'show')
                    ))
                    
        if conditions_to_create:
            ProductOptionCondition.objects.bulk_create(conditions_to_create)

    @transaction.atomic
    def update_product_option_config(self, product_id: int, product_option_id: int, data: dict):
        """
        [UPDATED] آپدیت تکی یک کانفیگ
        """
        try:
            prod_opt = ProductOption.objects.get(id=product_option_id, product_id=product_id)
        except ProductOption.DoesNotExist:
            raise InvalidProductDataException(f"ID نامعتبر: {product_option_id}")
        
        if 'is_required' in data: prod_opt.is_required = data['is_required']
        if 'guide_text' in data: prod_opt.guide_text = data['guide_text']
        if 'guide_type' in data: prod_opt.guide_type = data['guide_type']
        
        prod_opt.save()

        # آپدیت مقادیر (Values)
        if 'values' in data and data['values']:
            self._update_option_values_pricing_logic(product_id, product_option_id, data['values'])
            
        return prod_opt

    @transaction.atomic
    def _update_option_values_pricing_logic(self, product_id: int, product_option_id: int, updates: List[Dict]):
        from ..models import OptionValueQuantityPrice, ProductOptionCondition
        
        # ===== بارگذاری تمامی مقادیر فعلی محصول ===== #
        all_product_values = ProductOptionValue.objects.filter(product_option__product_id=product_id)
        
        # ===== مپ کردن تمامی شناسه ویژگی‌ها ===== #
        value_map_by_id = {v.id: v for v in all_product_values}
        
        # ===== دیکشنری برای ذخیره‌سازی ویژگی‌های جدید ===== #
        ref_map_new_values = {}

        # ===== تیراژ محصولات ===== #
        product_quantities = {pq.quantity_id: pq for pq in ProductQuantity.objects.filter(product_id=product_id)}

        to_update = []
        fields_to_update = ['price_impact', 'is_default', 'order', 'guide_text', 'guide_type', 'label', 'value']
        
        matrix_to_create = []
        pending_conditions = []

        for item in updates:
            val_id = item.get('id')
            ref_id = item.get('ref_id')
            
            # ===== آپدیت مقادیر موجود ===== #
            if val_id and val_id in value_map_by_id:
                obj = value_map_by_id[val_id]
                has_change = False

                for field in fields_to_update:
                    if field in item and getattr(obj, field) != item[field]:
                        setattr(obj, field, item[field])
                        has_change = True
                
                if has_change:
                    to_update.append(obj)
                    
            # ===== اگر مقدار جدید بود ===== #
            elif not val_id:
                label = item.get('label', 'Custom Option')
                obj = ProductOptionValue(
                    product_option_id=product_option_id,
                    global_source=None,
                    label=label,
                    value=item.get('value', label),
                    order=item.get('order', 0),
                    price_impact=item.get('price_impact', 0),
                    is_default=item.get('is_default', False),
                    guide_text=item.get('guide_text', ''),
                    guide_type=item.get('guide_type', 'info')
                )
                obj.save()
                
                value_map_by_id[obj.id] = obj
                if ref_id:
                    ref_map_new_values[ref_id] = obj

            if 'obj' in locals():
                # ===== تیراژها ===== #
                if 'quantity_prices' in item:
                    OptionValueQuantityPrice.objects.filter(option_value=obj).delete()
                    for qp in item['quantity_prices']:
                        pq = product_quantities.get(qp['quantity_id'])
                        if pq:
                            matrix_to_create.append(OptionValueQuantityPrice(
                                option_value=obj,
                                product_quantity=pq,
                                price=qp.get('price', 0)
                            ))

                # ===== جمع‌آوری ویژگی‌های شرطی ===== #
                if 'conditions' in item:
                    pending_conditions.append({
                        'target_obj': obj,
                        'conditions': item['conditions']
                    })

        if to_update:
            ProductOptionValue.objects.bulk_update(to_update, fields_to_update)
            
        if matrix_to_create:
            OptionValueQuantityPrice.objects.bulk_create(matrix_to_create)

        # ==========================================
        # مرحله دوم (Pass 2): اعمال قوانین وابستگی (Conditions)
        # ==========================================
        if pending_conditions:
            conditions_to_create = []
            
            for pending in pending_conditions:
                target_obj = pending['target_obj']
                
                # حذف شروط قبلی که این مقدار هدف آن‌ها بوده است
                ProductOptionCondition.objects.filter(target_value=target_obj).delete()
                
                for cond in pending['conditions']:
                    req_val_id = cond.get('required_value_id')
                    req_ref_id = cond.get('required_ref_id')
                    action = cond.get('action', 'show')
                    
                    req_obj = None
                    # پیدا کردن پیش‌نیاز (یا از مقادیر قبلی با ID، یا مقادیر جدید با ref_id)
                    if req_val_id and req_val_id in value_map_by_id:
                        req_obj = value_map_by_id[req_val_id]
                    elif req_ref_id and req_ref_id in ref_map_new_values:
                        req_obj = ref_map_new_values[req_ref_id]
                        
                    # جلوگیری از وابستگی یک ویژگی به هم‌گروه خودش
                    if req_obj and req_obj.product_option_id != target_obj.product_option_id:
                        conditions_to_create.append(ProductOptionCondition(
                            target_value=target_obj,
                            required_value=req_obj,
                            action=action
                        ))
                        
            if conditions_to_create:
                ProductOptionCondition.objects.bulk_create(conditions_to_create)
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
