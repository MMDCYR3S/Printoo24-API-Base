import os
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files import File
from django.utils import timezone

from core.models import (
    ProductCategory,
    Product,
    ProductCategoryRelation,
    ProductImage,
    FieldDictionary,
    FieldChoiceDictionary,
    ProductField,
    ProductFieldChoice,
    ProductFieldCondition,
    ProductFormula,
)

User = get_user_model()


# ============================================================ #
#  DATA MAP: تعریف فیلدهای مرجع (FieldDictionary) و مقادیرشان
# ============================================================ #

FIELD_DEFINITIONS = {
    'paper-type': {
        'title': 'نوع کاغذ',
        'field_type': 'dropdown',
        'is_quantity_field': False,
        'choices': [
            ('تحریر ۸۰ گرم', 0),
            ('گلاسه ۱۳۵ گرم', 15000),
            ('کرافت', 20000),
        ]
    },
    'corner-type': {
        'title': 'نوع گوشه',
        'field_type': 'single_select',
        'is_quantity_field': False,
        'choices': [
            ('تیز', 0),
            ('گرد معمولی', 5000),
            ('گرد شعاع ۵', 8000),
        ]
    },
    'coating': {
        'title': 'روکش',
        'field_type': 'single_select',
        'is_quantity_field': False,
        'choices': [
            ('بدون روکش', 0),
            ('سلفون مات', 10000),
            ('سلفون براق', 10000),
            ('UV موضعی', 25000),
        ]
    },
    'print-side': {
        'title': 'طرف چاپ',
        'field_type': 'single_select',
        'is_quantity_field': False,
        'choices': [
            ('یک رو', 0),
            ('دو رو', 20000),
        ]
    },
    'circulation': {
        'title': 'تیراژ',
        'field_type': 'dropdown',
        'is_quantity_field': True,
        'choices': [
            ('۱۰۰۰ عدد', 0),
            ('۲۰۰۰ عدد', 80000),
            ('۵۰۰۰ عدد', 180000),
        ]
    },
    'banner-material': {
        'title': 'جنس بنر',
        'field_type': 'single_select',
        'is_quantity_field': False,
        'choices': [
            ('ایرانی ۱۳ انس', 0),
            ('چینی', 15000),
            ('فلکس', 30000),
        ]
    },
    'delivery': {
        'title': 'زمان تحویل',
        'field_type': 'single_select',
        'is_quantity_field': False,
        'choices': [
            ('عادی ۷ روز', 0),
            ('فوری ۳ روز', 50000),
            ('اکسپرس ۲۴ ساعته', 120000),
        ]
    },
}


# ============================================================ #
#  تعریف الگوهای محصول و اینکه هر الگو چه فیلدهایی دارد
# ============================================================ #

PRODUCT_TEMPLATES = [
    {
        'name': 'کارت ویزیت گلاسه',
        'slug_base': 'glossy-business-card',
        'category_slugs': ['business-card'],
        'price': Decimal('150000'),
        'price_per_unit': 1000,
        'fields': ['paper-type', 'corner-type', 'coating', 'print-side', 'circulation', 'delivery'],
        'formula': '(base_price + paper_type_value + corner_type_value + coating_value + print_side_value + circulation_value) * 1',
        'is_large_format': False,
    },
    {
        'name': 'تراکت تحریر',
        'slug_base': 'paper-flyer',
        'category_slugs': ['flyer-80g', 'advertising-flyer'],
        'price': Decimal('80000'),
        'price_per_unit': 1000,
        'fields': ['paper-type', 'print-side', 'circulation', 'delivery'],
        'formula': '(base_price + paper_type_value + print_side_value + circulation_value)',
        'is_large_format': False,
    },
    {
        'name': 'تراکت گلاسه',
        'slug_base': 'glossy-flyer',
        'category_slugs': ['flyer-glossy-135', 'advertising-flyer'],
        'price': Decimal('120000'),
        'price_per_unit': 1000,
        'fields': ['coating', 'print-side', 'circulation', 'delivery'],
        'formula': '(base_price + coating_value + print_side_value + circulation_value)',
        'is_large_format': False,
    },
    {
        'name': 'بنر ایرانی',
        'slug_base': 'iranian-banner',
        'category_slugs': ['banner-13oz', 'banner-large-format'],
        'price': Decimal('45000'),
        'price_per_unit': 1,
        'fields': ['banner-material', 'delivery'],
        'formula': '(base_price + banner_material_value) * width * height',
        'is_large_format': True,
    },
    {
        'name': 'استیکر شیشه‌ای',
        'slug_base': 'glass-sticker',
        'category_slugs': ['sticker-glass', 'sticker-mesh'],
        'price': Decimal('60000'),
        'price_per_unit': 1,
        'fields': ['print-side', 'delivery'],
        'formula': '(base_price + print_side_value) * width * height',
        'is_large_format': True,
    },
    {
        'name': 'پاکت نامه ملخی',
        'slug_base': 'envelope-dl',
        'category_slugs': ['envelope-dl', 'office-set'],
        'price': Decimal('200000'),
        'price_per_unit': 1000,
        'fields': ['paper-type', 'print-side', 'circulation', 'delivery'],
        'formula': '(base_price + paper_type_value + print_side_value + circulation_value)',
        'is_large_format': False,
    },
    {
        'name': 'سربرگ A4',
        'slug_base': 'letterhead-a4',
        'category_slugs': ['letterhead-a4', 'office-set'],
        'price': Decimal('180000'),
        'price_per_unit': 1000,
        'fields': ['paper-type', 'coating', 'circulation', 'delivery'],
        'formula': '(base_price + paper_type_value + coating_value + circulation_value)',
        'is_large_format': False,
    },
    {
        'name': 'بروشور دو لت',
        'slug_base': 'brochure-2fold',
        'category_slugs': ['brochure-2-fold', 'brochure-catalog'],
        'price': Decimal('250000'),
        'price_per_unit': 1000,
        'fields': ['paper-type', 'coating', 'print-side', 'circulation', 'delivery'],
        'formula': '(base_price + paper_type_value + coating_value + circulation_value)',
        'is_large_format': False,
    },
    {
        'name': 'ساک دستی',
        'slug_base': 'shopping-bag',
        'category_slugs': ['shopping-bag', 'packaging'],
        'price': Decimal('500000'),
        'price_per_unit': 1000,
        'fields': ['paper-type', 'corner-type', 'circulation', 'delivery'],
        'formula': '(base_price + paper_type_value + corner_type_value + circulation_value)',
        'is_large_format': False,
    },
    {
        'name': 'مش چسب‌دار',
        'slug_base': 'mesh-adhesive',
        'category_slugs': ['mesh-adhesive', 'sticker-mesh'],
        'price': Decimal('55000'),
        'price_per_unit': 1,
        'fields': ['banner-material', 'delivery'],
        'formula': '(base_price + banner_material_value) * width * height',
        'is_large_format': True,
    },
]


class Command(BaseCommand):
    help = 'Seeds products based on actual model structure with FieldDictionary, ProductField, ProductFieldChoice, and ProductFormula'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('>>> شروع seed محصولات...'))

        # ===== آماده‌سازی تصاویر ===== #
        source_dir = os.path.join(settings.MEDIA_ROOT, 'pro')
        available_images = []
        if os.path.exists(source_dir):
            available_images = [
                f"{i}.jpg" for i in range(1, 9)
                if os.path.exists(os.path.join(source_dir, f"{i}.jpg"))
            ]

        if not available_images:
            self.stdout.write(self.style.WARNING(f"⚠️ هیچ تصویری در {source_dir} یافت نشد. محصولات بدون تصویر ساخته می‌شوند."))

        with transaction.atomic():

            # ===== ۱. بررسی ادمین ===== #
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR("❌ ادمین یافت نشد. ابتدا seed_categories را اجرا کنید."))
                return

            # ===== ۲. بررسی دسته‌بندی‌ها ===== #
            if not ProductCategory.objects.exists():
                self.stdout.write(self.style.ERROR("❌ دسته‌بندی یافت نشد. ابتدا seed_categories را اجرا کنید."))
                return

            # ===== ۳. ساخت FieldDictionary و FieldChoiceDictionary ===== #
            self.stdout.write(">>> ساخت فیلدهای مرجع...")
            field_dict_map = self._create_field_dictionaries()

            # ===== ۴. ساخت محصولات ===== #
            self.stdout.write(">>> ساخت محصولات...")
            count = 0
            for template in PRODUCT_TEMPLATES:
                # هر template را ۳ بار با ID تصادفی بساز
                for _ in range(3):
                    unique_id = random.randint(1000, 9999)
                    self._create_product(
                        admin_user,
                        template,
                        field_dict_map,
                        unique_id,
                        source_dir,
                        available_images,
                    )
                    count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ {count} محصول با موفقیت ساخته شد."))

    # ============================================================ #
    def _create_field_dictionaries(self):
        """
        ساخت یا دریافت FieldDictionary و FieldChoiceDictionary از دیتابیس.
        Returns: dict به شکل { 'paper-type': { 'obj': <FieldDictionary>, 'choices': { 'تحریر ۸۰ گرم': <FieldChoiceDictionary>, ... } } }
        """
        result = {}

        for key, data in FIELD_DEFINITIONS.items():
            field_obj, created = FieldDictionary.objects.get_or_create(
                title=data['title'],
                defaults={
                    'field_type': data['field_type'],
                    'is_quantity_field': data['is_quantity_field'],
                }
            )
            if created:
                self.stdout.write(f"  + FieldDictionary ساخته شد: {data['title']}")

            choices_map = {}
            for choice_title, numeric_val in data['choices']:
                choice_obj, _ = FieldChoiceDictionary.objects.get_or_create(
                    field=field_obj,
                    title=choice_title,
                )
                choices_map[choice_title] = {'obj': choice_obj, 'numeric_value': numeric_val}

            result[key] = {
                'obj': field_obj,
                'choices': choices_map,
            }

        return result

    # ============================================================ #
    def _create_product(self, user, template, field_dict_map, unique_id, source_dir, available_images):
        """ساخت یک محصول کامل با تمام روابط"""

        prod_name = f"{template['name']} - {unique_id}"
        prod_slug = f"{template['slug_base']}-{unique_id}"

        # ===== ۱. ساخت محصول پایه ===== #
        product = Product.objects.create(
            user=user,
            name=prod_name,
            slug=prod_slug,
            has_price=True,
            price=template['price'],
            price_per_unit=template['price_per_unit'],
            is_active=True,
            has_quantity=not template['is_large_format'],
            description=f"محصول {template['name']} با کیفیت تضمینی و تحویل سریع.",
        )

        # ===== ۲. اتصال دسته‌بندی‌ها از طریق جدول واسط ===== #
        for cat_slug in template['category_slugs']:
            try:
                cat = ProductCategory.objects.get(slug=cat_slug)
                ProductCategoryRelation.objects.get_or_create(
                    product=product,
                    category=cat,
                )
            except ProductCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  ⚠️ دسته‌بندی '{cat_slug}' یافت نشد، رد شد."))

        # ===== ۳. ساخت ProductField و ProductFieldChoice ===== #
        # نگه داشتن مپ از key فیلد به ProductField برای استفاده در فرمول و شرط
        product_field_map = {}

        for order_idx, field_key in enumerate(template['fields']):
            if field_key not in field_dict_map:
                continue

            field_data = field_dict_map[field_key]
            field_dict_obj = field_data['obj']

            # ساخت ProductField
            prod_field = ProductField.objects.create(
                product=product,
                field_dict=field_dict_obj,
                is_required=True,
                is_active=True,
                order=order_idx,
                numeric_value=Decimal('0.00'),
            )
            product_field_map[field_key] = prod_field

            # ساخت ProductFieldChoice برای هر گزینه
            for choice_idx, (choice_title, choice_data) in enumerate(field_data['choices'].items()):
                ProductFieldChoice.objects.create(
                    product_field=prod_field,
                    choice_dict=choice_data['obj'],
                    numeric_value=Decimal(str(choice_data['numeric_value'])),
                    is_default=(choice_idx == 0),
                    order=choice_idx,
                )

        # ===== ۴. ساخت شرط نمونه (ProductFieldCondition) ===== #
        # مثال: اگر روکش انتخاب شد و نوع کاغذ هم وجود داشت، شرط بساز
        if 'coating' in product_field_map and 'paper-type' in product_field_map:
            coating_field = product_field_map['coating']
            paper_field = product_field_map['paper-type']

            # گزینه پیش‌فرض coating (بدون روکش)
            default_coating_choice = ProductFieldChoice.objects.filter(
                product_field=coating_field,
                is_default=True
            ).first()

            if default_coating_choice:
                # اگر روکش = بدون روکش بود، فیلد کاغذ فعال بماند (نمونه شرط)
                ProductFieldCondition.objects.create(
                    target_field=paper_field,
                    trigger_field=coating_field,
                    operator='not_equals',
                    trigger_choice=default_coating_choice,
                    action='show',
                )

        # ===== ۵. ساخت فرمول قیمت‌گذاری (ProductFormula) ===== #
        ProductFormula.objects.create(
            product=product,
            title=f"فرمول اصلی - {product.name}",
            calculation_expression=template['formula'],
            condition_expression=None,
        )

        # ===== ۶. اتصال تصاویر ===== #
        if available_images:
            num_images = random.randint(3, min(5, len(available_images)))
            selected_imgs = random.sample(available_images, k=num_images)

            for img_order, img_name in enumerate(selected_imgs):
                try:
                    img_path = os.path.join(source_dir, img_name)
                    with open(img_path, 'rb') as f:
                        django_file = File(f)
                        prod_img = ProductImage(
                            user=user,
                            product=product,
                            order=img_order,
                        )
                        new_filename = f"prod_{product.id}_{unique_id}_{img_name}"
                        prod_img.image.save(new_filename, django_file, save=True)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ❌ خطا در تصویر {img_name}: {e}"))

        self.stdout.write(f"  + محصول ساخته شد: {prod_slug}")