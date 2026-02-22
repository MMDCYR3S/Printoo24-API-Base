from typing import List, Optional, Dict, Any
from django.db.models import Max, ProtectedError
from django.db import transaction
from django.utils import timezone

from ..exceptions import (
    ProductNotFoundException,
    InvalidProductDataException
)
from ..models import (
    Product, ProductCategory,
    ProductFormula, ProductFieldChoice, ProductField,
    ProductFieldCondition
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
    
    def get_product_detail_by_id(self, product_id: int) -> Dict[str, Any]:
        try:
            product = Product.objects.get_product_detail_by_id(product_id)
        except Product.DoesNotExist:
            raise ProductNotFoundException(f"محصول با شناسه {product_id} یافت نشد.")
        
        return {
            "product": product
            # "structured_options": self._format_product_options(product)
        }

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
        category_id = data.pop('category_id', None)
        category_ids = data.pop('category_ids', [])
        
        if category_id and category_id not in category_ids:
            category_ids.append(category_id)
        
        data['user'] = user
        product = Product.objects.create(**data)
        
        if category_ids:
            # استفاده از متد استاندارد ManyToMany جنگو
            product.categories.set(category_ids)
        
        return product

    @transaction.atomic
    def update_product_shell(self, pk: int, data: Dict[str, Any]) -> Product:
        product = Product.objects.get_by_id(pk)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")
        
        category_id = data.pop('category_id', None)
        category_ids = data.pop('category_ids', None)
        
        for key, value in data.items():
            setattr(product, key, value)
        product.save()
        
        # مدیریت آپدیت دسته‌بندی‌ها
        if category_ids is not None:
             product.categories.set(category_ids)
        elif category_id is not None:
             product.categories.set([category_id])
        
        return product

    # ===== ساخت بخش مربوط به محصولات ===== #
    def delete_product(self, product_id: int):
        product = Product.objects.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("محصول یافت نشد.")
        try:
            product.delete()
        except Exception:
            product.is_active = False
            product.save()

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

    # ========================================== #
    # 1. موتور همگام‌ساز فیلدها (Form Builder Sync)
    # ========================================== #
    @transaction.atomic
    def sync_fields(self, product_id: int, fields_data: List[Dict]):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ProductNotFoundException("محصول یافت نشد.")

        # --- پاک کردن فیلدهای حذف شده ---
        incoming_field_ids = [f['id'] for f in fields_data if f.get('id')]
        ProductField.objects.filter(product=product).exclude(id__in=incoming_field_ids).delete()

        pending_conditions = []
        
        # 🌟 تغییر کلیدی: دیکشنری‌های سراسری برای تمام فیلدها و گزینه‌های این محصول
        global_field_map = {}
        global_choice_map = {}

        # ======= مرحله اول (Pass 1): ساخت فیلدها و گزینه‌ها =======
        for field_data in fields_data:
            field_id = field_data.get('id')
            temp_id = field_data.get('temp_id')

            field_defaults = {
                'title': field_data['title'],
                'description': field_data.get('description', ''),
                'field_type': field_data['field_type'],
                'numeric_value': field_data.get('numeric_value', 0.0),
                'is_required': field_data.get('is_required', False),
                'is_active': field_data.get('is_active', True),
                'is_quantity_field': field_data.get('is_quantity_field', False),
                'order': field_data.get('order', 0),
            }

            if field_id:
                field, _ = ProductField.objects.update_or_create(
                    id=field_id, product=product, defaults=field_defaults
                )
            else:
                field = ProductField.objects.create(product=product, **field_defaults)

            # ثبت فیلد در ریجستری سراسری
            global_field_map[str(field.id)] = field
            if temp_id:
                global_field_map[str(temp_id)] = field

            # ذخیره گزینه‌ها (Choices)
            choices_data = field_data.get('choices', [])
            incoming_choice_ids = [c['id'] for c in choices_data if c.get('id')]
            ProductFieldChoice.objects.filter(field=field).exclude(id__in=incoming_choice_ids).delete()

            for choice_data in choices_data:
                choice_id = choice_data.get('id')
                temp_choice_id = choice_data.get('temp_id')
                
                choice_defaults = {
                    'title': choice_data['title'],
                    'numeric_value': choice_data.get('numeric_value', 0.0),
                    'order': choice_data.get('order', 0),
                }
                
                if choice_id:
                    choice, _ = ProductFieldChoice.objects.update_or_create(
                        id=choice_id, field=field, defaults=choice_defaults
                    )
                else:
                    choice = ProductFieldChoice.objects.create(field=field, **choice_defaults)

                # 🌟 ثبت گزینه در ریجستری سراسری (حل باگ اصلی)
                global_choice_map[str(choice.id)] = choice
                if temp_choice_id:
                    global_choice_map[str(temp_choice_id)] = choice

            # جمع‌آوری شرایط برای مرحله دوم (بدون نیاز به پاس دادن مپ‌ها)
            if field_data.get('conditions'):
                pending_conditions.append({
                    'target_field': field,
                    'conditions': field_data['conditions']
                })

        # ======= مرحله دوم (Pass 2): ساخت شرط‌ها با resolve کردن ID های موقت =======
        ProductFieldCondition.objects.filter(target_field__product=product).delete()

        new_conditions = []
        errors = []

        for pc in pending_conditions:
            target_field = pc['target_field']

            for cond_data in pc['conditions']:
                raw_trigger_field_id = str(cond_data['trigger_field_id'])
                raw_trigger_choice_id = str(cond_data.get('trigger_choice_id')) if cond_data.get('trigger_choice_id') else None

                # 1. Resolve کردن فیلد شرط از ریجستری سراسری
                trigger_field_obj = global_field_map.get(raw_trigger_field_id)
                if not trigger_field_obj:
                    errors.append(f"شرط فیلد '{target_field.title}': فیلد شرط با شناسه {raw_trigger_field_id} یافت نشد.")
                    continue

                # 2. Resolve کردن گزینه شرط از ریجستری سراسری
                resolved_choice_id = None
                if raw_trigger_choice_id and raw_trigger_choice_id != 'None':
                    choice_obj = global_choice_map.get(raw_trigger_choice_id)
                    if not choice_obj:
                        errors.append(f"شرط فیلد '{target_field.title}': گزینه شرط با شناسه {raw_trigger_choice_id} یافت نشد.")
                        continue
                    resolved_choice_id = choice_obj.id

                new_conditions.append(ProductFieldCondition(
                    target_field=target_field,
                    trigger_field=trigger_field_obj,
                    operator=cond_data['operator'],
                    trigger_choice_id=resolved_choice_id,
                    trigger_value_text=cond_data.get('trigger_value_text'),
                    action=cond_data['action']
                ))

        if errors:
            raise InvalidProductDataException({"condition_errors": errors})

        if new_conditions:
            ProductFieldCondition.objects.bulk_create(new_conditions)

        return True

    # ========================================== #
    # 2. موتور همگام‌ساز فرمول‌ها (Formula Builder Sync)
    # ========================================== #
    @transaction.atomic
    def sync_formulas(self, product_id: int, formulas_data: List[Dict]):
        """
        ذخیره‌سازی فرمول‌های ریاضی محصول
        """
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ProductNotFoundException("محصول یافت نشد.")

        # پاک کردن فرمول‌هایی که ادمین از لیست حذف کرده
        incoming_ids = [f['id'] for f in formulas_data if f.get('id')]
        ProductFormula.objects.filter(product=product).exclude(id__in=incoming_ids).delete()
        
        for form_data in formulas_data:
            form_id = form_data.get('id')
            defaults = {
                'title': form_data['title'],
                'condition_expression': form_data.get('condition_expression'),
                'calculation_expression': form_data['calculation_expression']
            }
            
            if form_id:
                ProductFormula.objects.update_or_create(id=form_id, product=product, defaults=defaults)
            else:
                ProductFormula.objects.create(product=product, **defaults)
                
        return True

