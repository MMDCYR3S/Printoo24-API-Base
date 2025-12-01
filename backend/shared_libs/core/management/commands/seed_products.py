import random
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.text import slugify
# ===== ایمپورت مدل‌ها (مسیر دقیق رو بر اساس پروژه‌ت تنظیم کن) ===== #
from core.models import (
    ProductCategory, Product, ProductPricingConfig,
    Size, ProductSize,
    Material, ProductMaterial,
    Quantity, ProductQuantity,
    ProductImage,
    Option, OptionValue, ProductOption,
    FileUploadSpec, ProductFileUploadRequirement,
    PricingType
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates 30 realistic products with full relations for testing.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Start seeding process...'))
        
        # ===== اجرای تمام عملیات در یک تراکنش برای حفظ یکپارچگی ===== #
        with transaction.atomic():
            user = self.get_or_create_superuser()
            
            # 1. ساخت دسته‌بندی‌ها
            categories = self.create_categories(user)
            
            # 2. ساخت سایزها
            sizes = self.create_sizes(user)
            
            # 3. ساخت متریال‌ها (کاغذ و ...)
            materials = self.create_materials(user)
            
            # 4. ساخت آپشن‌ها (مثل گوشه گرد، سلفون و ...)
            options_map = self.create_options(user)
            
            # 5. ساخت مشخصات آپلود فایل
            file_specs = self.create_file_specs()
            
            # 6. ساخت تیراژها
            quantities = self.create_quantities(user)

            # 7. ساخت محصولات اصلی
            self.create_products(
                user, categories, sizes, materials, 
                options_map, file_specs, quantities
            )

        self.stdout.write(self.style.SUCCESS('Successfully created 30 realistic products with full details.'))

    # ======== توابع کمکی (Helper Methods) ======== #

    def get_or_create_superuser(self):
        """ گرفتن یا ساختن یک کاربر برای انتساب رکوردها """
        user = User.objects.first()
        if not user:
            user = User.objects.create_superuser(
                username='admin_seeder', 
                email='admin@printoo24.com', 
                password='admin'
            )
            self.stdout.write(f'User created: {user.username}')
        return user

    def create_categories(self, user):
        """ ساخت ساختار درختی دسته‌بندی """
        root_names = ['کارت ویزیت', 'تراکت و بروشور', 'بنر و لارج فرمت', 'ست اداری']
        cats = []
        for name in root_names:
            cat, _ = ProductCategory.objects.get_or_create(
                name=name,
                defaults={'user': user, 'description': f'توضیحات مربوط به {name}'}
            )
            cats.append(cat)
            
            # ===== ساخت زیردسته ===== #
            for sub in ['مات', 'براق', 'کتان']:
                ProductCategory.objects.get_or_create(
                    name=f'{name} {sub}',
                    parent=cat,
                    defaults={'user': user}
                )
        
        # برگرداندن تمام دسته‌بندی‌های فرزند (برگ‌ها) برای اختصاص به محصول
        return ProductCategory.objects.exclude(parent=None)

    def create_sizes(self, user):
        """ ساخت سایزهای استاندارد چاپ """
        size_data = [
            ('کارت ویزیت استاندارد', 8.5, 4.8),
            ('کارت ویزیت مربع', 5.5, 5.5),
            ('A4', 21.0, 29.7),
            ('A5', 14.8, 21.0),
            ('تراکت A6', 10.5, 14.8),
            ('بنر 1x1', 100, 100),
        ]
        created_sizes = []
        for name, w, h in size_data:
            s, _ = Size.objects.get_or_create(
                name=name,
                defaults={'user': user, 'width': w, 'height': h}
            )
            created_sizes.append(s)
        return created_sizes

    def create_materials(self, user):
        """ ساخت متریال (کاغذ/جنس) """
        materials_data = [
            ('گلاسه ۳۰۰ گرم', 15000),
            ('تحریر ۸۰ گرم', 5000),
            ('کتان آلمان', 25000),
            ('سلفون مات', 12000),
            ('لمینت براق', 40000),
        ]
        created_materials = []
        for name, price in materials_data:
            m, _ = Material.objects.get_or_create(
                name=name,
                defaults={
                    'user': user, 
                    'price_per_sqm': Decimal(price),
                    'description': f'توضیحات فنی برای {name}'
                }
            )
            created_materials.append(m)
        return created_materials

    def create_options(self, user):
        """ ساخت آپشن‌ها و مقادیر آن‌ها """
        # مپ: نام آپشن -> لیست مقادیر
        options_source = {
            'نوع گوشه': ['تیز', 'گرد (Round)', 'گرد (Super Round)'],
            'خدمات پس از چاپ': ['بدون روکش', 'یووی موضعی', 'طلاکوب'],
            'زمان تحویل': ['عادی (۷ روز کاری)', 'فوری (۲ روز کاری)', 'آنی (۵ ساعته)']
        }
        
        final_map = {} # Key: OptionObj, Value: [OptionValueObj, ...]
        
        for opt_name, values in options_source.items():
            opt, _ = Option.objects.get_or_create(
                name=opt_name, 
                defaults={'user': user}
            )
            val_objs = []
            for val in values:
                v_obj, _ = OptionValue.objects.get_or_create(
                    option=opt, 
                    value=val, 
                    defaults={'user': user}
                )
                val_objs.append(v_obj)
            final_map[opt] = val_objs
            
        return final_map

    def create_file_specs(self):
        names = ['طرح رو (Front)', 'طرح پشت (Back)', 'فایل خط برش', 'فایل یووی']
        specs = []
        for n in names:
            obj, _ = FileUploadSpec.objects.get_or_create(name=n)
            specs.append(obj)
        return specs

    def create_quantities(self, user):
        values = [1000, 2000, 5000, 10000]
        objs = []
        for v in values:
            q, _ = Quantity.objects.get_or_create(value=v, defaults={'user': user})
            objs.append(q)
        return objs

    def create_products(self, user, categories, sizes, materials, options_map, file_specs, quantities):
        """ تابع اصلی ساخت ۳۰ محصول """
        
        product_names_base = [
            'کارت ویزیت لاکچری', 'تراکت تبلیغاتی رنگی', 'سربرگ اداری', 
            'پاکت نامه ملخی', 'بنر مناسبتی', 'استیکر شیشه‌ای', 
            'کاتالوگ دیجیتال', 'فاکتور فروش', 'برچسب اموال'
        ]

        # ===== لیست تصاویر (طبق گفته شما در پوشه مدیا هستند) ===== #
        # فرض بر این است که فایل‌ها در media/pro/1.jpg تا media/pro/7.jpg وجود دارند
        image_paths = [f'pro/{i}.jpg' for i in range(1, 8)]

        for i in range(1, 31):
            base_name = random.choice(product_names_base)
            category = random.choice(categories)
            
            prod_name = f"{base_name} - مدل {random.randint(100, 999)}"
            
            # ===== 1. ساخت محصول ===== #
            product = Product.objects.create(
                user=user,
                name=prod_name,
                category=category,
                price=random.randint(50000, 500000), # قیمت پایه محصول
                description=f"این یک توضیحات تست برای محصول {prod_name} است. کیفیت بالا و چاپ عالی.",
                price_per_square_unit=Decimal(random.randint(100, 1000)) if 'بنر' in base_name else None,
                has_quantity=True,
                is_active=True
            )
            
            # ===== 2. ساخت کانفیگ قیمت ===== #
            ProductPricingConfig.objects.create(
                product=product,
                allow_custom_quantity=random.choice([True, False]),
                min_quantity=100,
                max_quantity=50000,
                accepts_custom_dimensions=True if 'بنر' in base_name else False,
                base_setup_price=Decimal(random.choice([0, 50000, 100000])),
                design_service_available=True,
                design_fee=Decimal(150000)
            )
            
            # ===== 3. انتساب تصاویر (چند تصویر برای هر محصول) ===== #
            # انتخاب 2 یا 3 عکس رندوم از لیست موجود
            selected_images = random.sample(image_paths, k=random.randint(2, 4))
            for idx, img_path in enumerate(selected_images):
                ProductImage.objects.create(
                    user=user,
                    product=product,
                    image=img_path, # مسیر نسبی در پوشه مدیا
                    order=idx
                )

            # ===== 4. انتساب سایزها ===== #
            # هر محصول ۳ سایز داشته باشد
            selected_sizes = random.sample(sizes, k=3)
            for size in selected_sizes:
                ProductSize.objects.create(
                    user=user,
                    product=product,
                    size=size,
                    price_impact=Decimal(random.choice([0, 10000, 20000]))
                )

            # ===== 5. انتساب متریال‌ها ===== #
            selected_materials = random.sample(materials, k=2)
            for mat in selected_materials:
                ProductMaterial.objects.create(
                    user=user,
                    product=product,
                    material=mat,
                    is_default=random.choice([True, False]),
                    processing_fee_percentage=Decimal(random.randint(0, 20)),
                    extra_price_per_unit=Decimal(random.choice([0, 5000]))
                )

            # ===== 6. انتساب آپشن‌ها ===== #
            # از هر گروه آپشن، یکی دو مقدار رو برای محصول ست می‌کنیم
            for opt, values in options_map.items():
                selected_vals = random.sample(values, k=random.randint(1, len(values)))
                for val in selected_vals:
                    ProductOption.objects.create(
                        user=user,
                        product=product,
                        option=opt,
                        option_value=val,
                        pricing_type=random.choice(PricingType.choices)[0],
                        price_impact=Decimal(random.randint(1000, 50000)),
                        is_required=random.choice([True, False])
                    )
            
            # ===== 7. انتساب تیراژ ===== #
            for q in quantities:
                ProductQuantity.objects.create(
                    user=user,
                    product=product,
                    quantity=q,
                    price=product.price + random.randint(100000, 2000000) # قیمت کل برای اون تیراژ
                )
            
            # ===== 8. نیازمندی‌های فایل ===== #
            req_specs = random.sample(file_specs, k=2)
            for idx, spec in enumerate(req_specs):
                ProductFileUploadRequirement.objects.create(
                    product=product,
                    spec=spec,
                    is_required=True,
                    sort_order=idx
                )

            self.stdout.write(f'Created Product: {product.name}')
