import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.text import slugify

# ===== ایمپورت مدل‌های نهایی ===== #
from core.models import (
    ProductCategory, Product, ProductPricingConfig,
    Size, ProductSize,
    Quantity, ProductQuantity,
    Option, ProductOption, ProductOptionValue
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates products compatible with M2M architecture and English Slugs.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('>>> Start seeding products...'))
        
        with transaction.atomic():
            # 1. ادمین
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR("ادمین یافت نشد. ابتدا seed_categories را اجرا کنید."))
                return

            # 2. دریافت دسته‌بندی‌ها (فقط فرزندان)
            categories = ProductCategory.objects.exclude(parent=None)
            if not categories.exists():
                self.stdout.write(self.style.ERROR("دسته‌بندی یافت نشد."))
                return

            # 3. ساخت داده‌های مرجع (سایز، آپشن، تیراژ)
            sizes = self.create_master_sizes(admin_user)
            options_dict = self.create_master_options(admin_user)
            quantities = self.create_master_quantities(admin_user)
            
            # 4. ساخت محصولات
            self.create_products(admin_user, categories, sizes, options_dict, quantities)

        self.stdout.write(self.style.SUCCESS('✅ 30 Products created successfully.'))

    # ==================== HELPERS ==================== #

    def create_master_sizes(self, user):
        data = [('Standard Card', 8.5, 4.8), ('Square Card', 5.5, 5.5), ('A4', 21.0, 29.7), ('A5', 14.8, 21.0)]
        return [Size.objects.get_or_create(name=n, defaults={'user': user, 'width': w, 'height': h})[0] for n, w, h in data]

    def create_master_options(self, user):
        # کلید انگلیسی برای اسلاگ، مقدار فارسی برای لیبل
        source = {
            'corner-type': {'label': 'نوع گوشه', 'type': 'select', 'values': ['تیز', 'گرد معمولی', 'گرد شعاع ۵']},
            'coating': {'label': 'روکش', 'type': 'radio', 'values': ['سلفون مات', 'سلفون براق', 'بدون روکش']},
            'delivery': {'label': 'زمان تحویل', 'type': 'radio', 'values': ['عادی (۷ روز)', 'فوری (۲ روز)']},
        }
        result = {}
        for key, data in source.items():
            opt, _ = Option.objects.get_or_create(
                name=key, # Slug انگلیسی
                defaults={'label': data['label'], 'input_type': data['type']}
            )
            result[key] = {'obj': opt, 'values': data['values']}
        return result

    def create_master_quantities(self, user):
        return [Quantity.objects.get_or_create(value=v, defaults={'user': user})[0] for v in [1000, 2000, 5000]]

    # ==================== MAIN LOGIC ==================== #

    def create_products(self, user, categories, sizes, options_map, quantities):
        # قالب: (نام فارسی، اسلاگ انگلیسی پایه، آیا لارج فرمت است؟)
        product_templates = [
            ('کارت ویزیت گلاسه', 'glossy-business-card', False),
            ('تراکت تحریر', 'paper-flyer', False),
            ('بنر تسلیت', 'banner-condolence', True),
            ('استیکر شیشه‌ای', 'glass-sticker', True),
            ('پاکت نامه ملخی', 'envelope-dl', False)
        ]

        for i in range(1, 31):
            name_fa, slug_base, is_large = random.choice(product_templates)
            cat = random.choice(categories)
            
            # تولید نام و اسلاگ یونیک
            unique_id = random.randint(1000, 9999)
            prod_name = f"{name_fa} - نمونه {unique_id}"
            prod_slug = f"{slug_base}-{unique_id}"

            # 1. ساخت محصول (بدون Category)
            product = Product.objects.create(
                user=user,
                # category=cat,  <--- حذف شد (M2M Fix)
                name=prod_name,
                slug=prod_slug, # اسلاگ انگلیسی دستی
                has_price=True,
                price=Decimal(random.choice([50000, 100000])),
                price_per_unit=1 if is_large else 1000,
                is_active=True,
                has_quantity=not is_large,
                # کد موقت تولید می‌شود، سیگنال بعداً آپدیت می‌کند
            )

            # 2. اتصال دسته‌بندی (M2M Fix)
            # این خط باعث تریگر شدن سیگنال و تولید کد محصول نهایی می‌شود
            product.categories.add(cat)

            # 3. کانفیگ قیمت
            ProductPricingConfig.objects.create(
                product=product,
                allow_custom_quantity=is_large,
                min_quantity=1 if is_large else 1000,
                max_quantity=50000,
                accepts_custom_dimensions=is_large,
                min_width=10.0 if is_large else 0,
                max_width=500.0 if is_large else 0,
                base_setup_price=Decimal(50000)
            )

            # 4. اتصال سایز و تیراژ (اگر لارج فرمت نیست)
            if not is_large:
                for s in random.sample(sizes, k=min(2, len(sizes))):
                    ProductSize.objects.create(user=user, product=product, size=s, price_impact=0)
                
                for q in quantities:
                    ProductQuantity.objects.create(
                        user=user, product=product, quantity=q
                    )

            # 5. اتصال آپشن‌ها
            selected_keys = random.sample(list(options_map.keys()), k=random.randint(1, 2))
            for idx, key in enumerate(selected_keys):
                opt_data = options_map[key]
                prod_opt = ProductOption.objects.create(
                    product=product,
                    option=opt_data['obj'],
                    is_required=True,
                    order=idx
                )
                
                # مقادیر آپشن
                for v_idx, v_label in enumerate(opt_data['values']):
                    ProductOptionValue.objects.create(
                        product_option=prod_opt,
                        label=v_label,
                        value=v_label, # مقدار فارسی در ولیو (چون نمایشی است)
                        price_impact=Decimal(random.randint(0, 20000)),
                        is_default=(v_idx==0),
                        order=v_idx
                    )

            self.stdout.write(f" + Product: {prod_slug} -> Category: {cat.slug}")