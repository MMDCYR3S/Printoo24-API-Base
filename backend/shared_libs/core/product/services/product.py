import ast
import re
from typing import List, Optional, Dict, Any, Set

from django.db.models import Max, ProtectedError
from django.db import transaction
from django.utils import timezone

from ..exceptions import (
    ProductNotFoundException,
    InvalidProductDataException,
    ProductHasDependencyException
)
from ..models import (
    Product, ProductCategory,
    ProductFormula, ProductFieldChoice, ProductField, FieldChoiceDictionary,
    ProductFieldCondition, ProductCategoryRelation, FieldDictionary
)

from ..schemas import CategoryAssignment

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
        categories = data.pop('categories', [])
        
        data['user'] = user
        product = Product.objects.create(**data)

        assignments = [
            CategoryAssignment(
                category_id=item['category_id'],
                is_primary=item.get('is_primary', False),
                priority=item.get('priority', 3),
                order=item.get('order', 0)
            )
            for item in categories
        ]
        self._sync_categories(product, assignments)
        return product

    @transaction.atomic
    def update_product_shell(self, pk: int, data: Dict[str, Any]) -> Product:
        product = Product.objects.get_by_id(pk)
        if not product:
            raise ProductNotFoundException("...")
        
        categories = data.pop('categories', None)
        
        for key, value in data.items():
            setattr(product, key, value)
        product.save()
        
        if categories is not None:
            assignments = [
                CategoryAssignment(
                    category_id=item['category_id'],
                    is_primary=item.get('is_primary', False),
                    priority=item.get('priority', 3),
                    order=item.get('order', 0)
                )
                for item in categories
            ]
            self._sync_categories(product, assignments)
        
        return product
    
    def _sync_categories(self, product, category_assignments: List[CategoryAssignment]):
        """ مدیریت صریح یک دسته اصلی و یک زیردسته """
        ProductCategoryRelation.objects.filter(product=product).delete()

        relations_to_create = []
        for ass in category_assignments:
            relations_to_create.append(
                ProductCategoryRelation(
                    product=product,
                    category_id=ass.category_id,
                    is_primary=ass.is_primary,
                    priority=ass.priority,
                    order=ass.order
                )
            )

        if relations_to_create:
            ProductCategoryRelation.objects.bulk_create(relations_to_create)

        primary_relations = ProductCategoryRelation.objects.filter(product=product, is_primary=True)
        if primary_relations.count() > 1:
            # ===== نگهداری یک دسته‌بندی اصلی و باقی آن‌ها، عادی شوند. ===== #
            first = primary_relations.first()
            ProductCategoryRelation.objects.filter(product=product, is_primary=True).exclude(pk=first.pk).update(is_primary=False)

    # ===== ساخت بخش مربوط به محصولات ===== #
    def delete_product(self, product_id: int):
        product = Product.objects.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException("بەرهەمی دیاریکراو نەدۆزرایەوە.")
        try:
            product.delete()
        except ProtectedError:
            raise ProductHasDependencyException("این محصول در بخش‌های دیگر (مانند سفارشات) وابستگی دارد و قابل حذف نیست.")
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

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""
        text = text.strip()
        text = text.replace('ي', 'ی').replace('ك', 'ک')
        text = re.sub(r'\s+', ' ', text)
        return text

    # ========================================== #
    # 1. موتور همگام‌ساز فیلدها (Form Builder Sync)
    # ========================================== #
    @transaction.atomic
    def sync_fields(self, product_id: int, fields_data: List[Dict]):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ProductNotFoundException("بەرهەمی دیاریکراو نەدۆزرایەوە.")

        # --- پاک کردن فیلدهای حذف شده ---
        clean_fields_data = [
            f for f in fields_data 
            if str(f.get('id')) != 'base_price' and str(f.get('temp_id')) != 'base_price'
        ]

        incoming_field_ids = [f['id'] for f in clean_fields_data if f.get('id')]
        # حذف از جدول واسط (دیکشنری‌ها دست‌نخورده باقی می‌مانند)
        ProductField.objects.filter(product=product).exclude(id__in=incoming_field_ids).delete()

        pending_conditions = []
        global_field_map = {}
        global_choice_map = {}

        # ======= مرحله اول (Pass 1): ساخت فیلدها و گزینه‌ها ======= #
        for field_data in clean_fields_data:
            field_id = field_data.get('id')
            temp_id = field_data.get('temp_id')

            # ===== پردازش لایه دیکشنری فیلد ===== #
            clean_field_title = self.normalize_text(field_data.get('title', ''))

            # ===== مشخصاتی که فرانت‌اندن فرستاده است ===== #

            field_dict, _ = FieldDictionary.objects.update_or_create(
                title=clean_field_title,
                defaults={
                    'description': field_data.get('description', ''),
                    'field_type': field_data.get('field_type', 'dropdown'),
                    'multi_select_operator': field_data.get('multi_select_operator', 'add'),
                    'is_quantity_field': field_data.get('is_quantity_field', False),
                }
            )

            # ===== پردازش لایه واسط فیلد - اتصال به محصول ===== #
            product_field_defaults = {
                'field_dict': field_dict,
                'numeric_value': field_data.get('numeric_value', 0.0),
                'is_required': field_data.get('is_required', False),
                'is_active': field_data.get('is_active', True),
                'order': field_data.get('order', 0),
            }

            if field_id:
                product_field, _ = ProductField.objects.update_or_create(
                    id=field_id, product=product, defaults=product_field_defaults
                )
            else:
                product_field = ProductField.objects.create(product=product, **product_field_defaults)

            # ===== ثبت فیلد در یک مخزن سراسری که تعبیه شده است ===== #
            global_field_map[str(product_field.id)] = product_field
            if temp_id:
                global_field_map[str(temp_id)] = product_field

            # ===== پردازش انتخاب‌ها ===== #
            choices_data = field_data.get('choices', [])
            incoming_choice_ids = [c['id'] for c in choices_data if c.get('id')]
            ProductFieldChoice.objects.filter(product_field=product_field).exclude(id__in=incoming_choice_ids).delete()

            for choice_data in choices_data:
                choice_id = choice_data.get('id')
                temp_choice_id = choice_data.get('temp_id')
                
                # ===== پردازش دیکشنری انتخاب‌ها ===== #
                clean_choice_title = self.normalize_text(choice_data.get('title', ''))
                choice_dict, _ = FieldChoiceDictionary.objects.get_or_create(
                    field=field_dict,
                    title=clean_choice_title
                )

                # ===== اتصال انتخاب‌ها به فیلد محصول ===== #
                product_choice_defaults = {
                    'choice_dict': choice_dict,
                    'numeric_value': choice_data.get('numeric_value', 0.0),
                    'order': choice_data.get('order', 0),
                    'is_default': choice_data.get('is_default', False)
                }
                
                if choice_id:
                    product_choice, _ = ProductFieldChoice.objects.update_or_create(
                        id=choice_id, product_field=product_field, defaults=product_choice_defaults
                    )
                else:
                    product_choice = ProductFieldChoice.objects.create(product_field=product_field, **product_choice_defaults)

                # ثبت گزینه در ریجستری سراسری
                global_choice_map[str(product_choice.id)] = product_choice
                if temp_choice_id:
                    global_choice_map[str(temp_choice_id)] = product_choice

            # جمع‌آوری شرایط برای مرحله دوم
            if field_data.get('conditions'):
                pending_conditions.append({
                    'target_field': product_field,
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

                trigger_field_obj = global_field_map.get(raw_trigger_field_id)
                if not trigger_field_obj:
                    errors.append(f"شرط فیلد '{target_field.field_dict.title}': فیلد شرط یافت نشد.")
                    continue

                resolved_choice_id = None
                if raw_trigger_choice_id and raw_trigger_choice_id != 'None':
                    choice_obj = global_choice_map.get(raw_trigger_choice_id)
                    if not choice_obj:
                        errors.append(f"شرط فیلد '{target_field.field_dict.title}': گزینه شرط یافت نشد.")
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
    def _validate_math_expression(self, expression: str, valid_variables: Set[str]):
        """
        هسته اعتبارسنجی امن فرمول. 
        فقط اجازه ورود متغیرهای مجاز و عملگرهای ریاضی را می‌دهد.
        """
        if not expression:
            return

        try:
            # ===== بررسی اعتبار رشته براساس قواعد ریاضیاتی ===== #
            tree = ast.parse(expression, mode='eval')
        except SyntaxError:
            raise InvalidProductDataException(f"ساختار فرمول نامعتبر است (لطفاً علائم ریاضی را چک کنید): {expression}")

        # پیمایش تمام اجزای فرمول
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                var_name = node.id
                # ===== در صورت عدم انتخاب فیلدهای معتبر یک محصول، خطا دادن ===== #
                if var_name not in valid_variables:
                    raise InvalidProductDataException(
                        f"متغیر ناشناخته '{var_name}' در فرمول. شما فقط مجاز به استفاده از شناسه‌های فیلد همین محصول هستید (مثلاً: field_12)."
                    )
            elif isinstance(node, ast.Call):
                # ===== خطا در صورت استفاده از توابع ===== #
                raise InvalidProductDataException("استفاده از توابع (Functions) در فرمول مجاز نیست.")

    @transaction.atomic
    def sync_formulas(self, product_id: int, formulas_data: List[Dict]):
        """
        ذخیره‌سازی فرمول‌های ریاضی محصول همراه با اعتبارسنجی شدید
        """
        try:
            product = Product.objects.prefetch_related('fields').get(id=product_id)
        except Product.DoesNotExist:
            raise ProductNotFoundException("محصول یافت نشد.")

        # ===== استخراج فیلدهای مجاز با field_{id} ===== # 
        valid_variables = {f"field_{f.id}" for f in product.fields.all()}
        valid_variables.add("price_per_unit")

        # ===== اعتبارسنجی فرمول‌ها ===== #
        for form_data in formulas_data:
            calc_expr = form_data.get('calculation_expression', '')
            cond_expr = form_data.get('condition_expression', '')

            if not calc_expr:
                raise InvalidProductDataException("عبارت محاسباتی (calculation_expression) نمی‌تواند خالی باشد.")

            # ===== اعتبارسنجی فرمول‌ها اصلی و فرعی ===== #
            self._validate_math_expression(calc_expr, valid_variables)
            if cond_expr:
                self._validate_math_expression(cond_expr, valid_variables)

        # ===== ذخیره‌سازی فرمول‌ها در دیتابیس ===== #
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

    # ========================================== #
    # 3. موتور کپی‌ساز (Product Duplication)
    # ========================================== #
    @transaction.atomic
    def duplicate_product(self, product_id: int, user) -> Product:
        """
        کپی کردن کامل یک محصول شامل:
        اطلاعات پایه، دسته‌بندی‌ها، فیلدها، گزینه‌ها، شروط و فرمول‌ها.
        نکته: تصاویر و فایل‌های پیوست کپی نمی‌شوند.
        """
        try:
            # بارگذاری محصول به همراه روابط مورد نیاز برای جلوگیری از N+1
            original_product = Product.objects.prefetch_related(
                'category_relations',
                'fields__choices',
                'formulas'
            ).get(id=product_id)
        except Product.DoesNotExist:
            raise ProductNotFoundException("محصول مورد نظر برای کپی یافت نشد.")

        # ۱. کپی کردن پوسته اصلی محصول (Shell)
        # پیشنهاد می‌شود محصول کپی شده در حالت غیرفعال باشد تا کاربر پس از بررسی آن را فعال کند
        new_name = f"{original_product.name} (کپی)"
        new_product = Product.objects.create(
            user=user,  # کاربری که درخواست کپی داده است
            name=new_name,
            has_price=original_product.has_price,
            show_price=original_product.show_price,
            price=original_product.price,
            price_per_unit=original_product.price_per_unit,
            description=original_product.description,
            is_active=False, # غیرفعال به صورت پیش‌فرض
            has_quantity=original_product.has_quantity,
            guide_text=original_product.guide_text,
            guide_type=original_product.guide_type
            # فیلدهای slug و code به صورت خودکار توسط متد save مدل تولید می‌شوند
        )

        # ۲. کپی کردن روابط دسته‌بندی
        category_relations = [
            ProductCategoryRelation(product=new_product, category_id=rel.category_id)
            for rel in original_product.category_relations.all()
        ]
        if category_relations:
            ProductCategoryRelation.objects.bulk_create(category_relations)

        # ۳. کپی کردن فیلدها و مقادیر (با نگهداری نقشه تغییرات ID)
        old_to_new_field_ids = {}
        old_to_new_choice_ids = {}

        for old_field in original_product.fields.all():
            new_field = ProductField.objects.create(
                product=new_product,
                field_dict_id=old_field.field_dict_id,
                numeric_value=old_field.numeric_value,
                is_required=old_field.is_required,
                is_active=old_field.is_active,
                order=old_field.order
            )
            # ثبت نگاشت ID قدیم به جدید برای فیلدها
            old_to_new_field_ids[old_field.id] = new_field.id

            # کپی کردن گزینه‌های این فیلد
            for old_choice in old_field.choices.all():
                new_choice = ProductFieldChoice.objects.create(
                    product_field=new_field,
                    choice_dict_id=old_choice.choice_dict_id,
                    numeric_value=old_choice.numeric_value,
                    is_default=old_choice.is_default,
                    order=old_choice.order
                )
                # ثبت نگاشت ID قدیم به جدید برای گزینه‌ها
                old_to_new_choice_ids[old_choice.id] = new_choice.id

        # ۴. کپی کردن شروط (Conditions) با ترجمه IDها
        original_conditions = ProductFieldCondition.objects.filter(target_field__product=original_product)
        new_conditions = []
        
        for old_cond in original_conditions:
            # پیدا کردن ID جدید برای trigger_choice (در صورت وجود)
            new_trigger_choice_id = None
            if old_cond.trigger_choice_id:
                new_trigger_choice_id = old_to_new_choice_ids.get(old_cond.trigger_choice_id)

            # اگر فیلد هدف یا شرط به هر دلیلی در مپ نبودند، از آن شرط رد می‌شویم
            if old_cond.target_field_id not in old_to_new_field_ids or old_cond.trigger_field_id not in old_to_new_field_ids:
                continue

            new_conditions.append(
                ProductFieldCondition(
                    target_field_id=old_to_new_field_ids[old_cond.target_field_id],
                    trigger_field_id=old_to_new_field_ids[old_cond.trigger_field_id],
                    operator=old_cond.operator,
                    trigger_choice_id=new_trigger_choice_id,
                    trigger_value_text=old_cond.trigger_value_text,
                    action=old_cond.action
                )
            )
        
        if new_conditions:
            ProductFieldCondition.objects.bulk_create(new_conditions)

        # ۵. کپی کردن فرمول‌ها (Formulas) و ترجمه متغیرها در عبارت‌های ریاضی
        new_formulas = []
        for old_formula in original_product.formulas.all():
            new_calc_expr = old_formula.calculation_expression or ""
            new_cond_expr = old_formula.condition_expression or ""

            # جایگزینی امن با استفاده از Regex (ترجمه field_X به field_Y)
            # از \b استفاده می‌شود تا کلماتی مثل field_12 با field_1 اشتباه گرفته نشوند
            for old_id, new_id in old_to_new_field_ids.items():
                pattern = rf"\bfield_{old_id}\b"
                replacement = f"field_{new_id}"
                
                if new_calc_expr:
                    new_calc_expr = re.sub(pattern, replacement, new_calc_expr)
                if new_cond_expr:
                    new_cond_expr = re.sub(pattern, replacement, new_cond_expr)
            
            new_formulas.append(
                ProductFormula(
                    product=new_product,
                    title=old_formula.title,
                    condition_expression=new_cond_expr,
                    calculation_expression=new_calc_expr
                )
            )
        
        if new_formulas:
            ProductFormula.objects.bulk_create(new_formulas)

        return new_product

