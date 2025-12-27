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
    ProductImage,
    Option, OptionPricingStrategy, 
    ProductOption, ProductOptionValue,
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates 30 realistic products compatible with the NEW architecture.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('>>> Start seeding products...'))
        
        with transaction.atomic():
            # 1. ادمین سیستم
            admin_user = self.get_or_create_superuser()
            
            # 2. بررسی دسته‌بندی‌ها
            categories = ProductCategory.objects.exclude(parent=None)
            if not categories.exists():
                self.stdout.write(self.style.ERROR("لطفا ابتدا دستور seed_categories را اجرا کنید."))
                return

            # 3. ساخت سایزهای استاندارد
            sizes = self.create_master_sizes(admin_user) 
            
            # 4. ساخت آپشن‌های (ویژگی‌های) مرجع
            options_dict = self.create_master_options(admin_user)
            
            # 5. ساخت تیراژهای مرجع
            quantities = self.create_master_quantities(admin_user)
            
            # 6. ساخت محصولات اصلی
            self.create_products(
                admin_user, categories, sizes, 
                options_dict, quantities
            )

        self.stdout.write(self.style.SUCCESS('✅ Successfully created 30 realistic products.'))

    # ==========================================
    # HELPER METHODS (Master Data)
    # ==========================================

    def get_or_create_superuser(self):
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            # اگر وجود نداشت یکی بساز
            user = User.objects.create_superuser('admin', 'admin@printoo24.ir', 'admin')
        return user

    def create_master_sizes(self, user):
        """ سایزهای استاندارد """
        data = [
            ('کارت ویزیت استاندارد', 8.5, 4.8),
            ('کارت ویزیت مربع', 5.5, 5.5),
            ('A4', 21.0, 29.7),
            ('A5', 14.8, 21.0),
            ('تراکت A6', 10.5, 14.8),
            ('بنر 1x1', 100, 100),
        ]
        objs = []
        for name, w, h in data:
            s, _ = Size.objects.get_or_create(
                name=name, 
                defaults={'user': user, 'width': w, 'height': h}
            )
            objs.append(s)
        return objs

    def create_master_options(self, user):
        """ ساخت آپشن‌های مرجع """
        source = {
            'نوع گوشه': ('select', ['تیز', 'گرد معمولی', 'گرد شعاع ۵']),
            'خدمات پس از چاپ': ('checkbox', ['یووی موضعی', 'طلاکوب', 'نقره‌کوب']),
            'زمان تحویل': ('radio', ['عادی (۷ روز)', 'فوری (۲ روز)', 'آنی (۵ ساعت)']),
            'متن اختصاصی': ('text', []), 
            'تعداد پانچ': ('number', []),
        }
        
        result_map = {}
        for name, (input_type, values) in source.items():
            opt, _ = Option.objects.get_or_create(
                name=slugify(name, allow_unicode=True),
                defaults={
                    'label': name, 
                    'input_type': input_type
                    # توجه: مدل Option فیلد user ندارد (طبق کد ارسالی شما)
                    # اگر دارد، اینجا اضافه کنید: 'user': user
                }
            )
            result_map[name] = {'obj': opt, 'values': values}
            
        return result_map

    def create_master_quantities(self, user):
        values = [1000, 2000, 5000, 10000]
        objs = []
        for v in values:
            q, _ = Quantity.objects.get_or_create(
                value=v,
                defaults={'user': user}
            )
            objs.append(q)
        return objs


    # ==========================================
    # CORE PRODUCT CREATION
    # ==========================================

    def create_products(self, user, categories, sizes, options_map, quantities):
        
        # قالب: (نام، آیا لارج فرمت است؟، گام شمارش)
        product_bases = [
            ('کارت ویزیت لاکچری', False, 1000), 
            ('تراکت تبلیغاتی', False, 1000), 
            ('بنر مناسبتی', True, 1), 
            ('استیکر شیشه‌ای', True, 1), 
            ('سربرگ اداری', False, 1000), 
            ('پاکت نامه ملخی', False, 1000)
        ]

        # عکس‌های تستی (فرض بر این است که فایل‌ها وجود دارند)
        # برای جلوگیری از ارور فایل، از یک لیست ساده استفاده می‌کنیم
        image_pool = [f'products/sample_{i}.jpg' for i in range(1, 4)]

        for i in range(1, 31):
            base_name, is_large_format, unit_step = random.choice(product_bases)
            cat = random.choice(categories)
            prod_name = f"{base_name} - نمونه {random.randint(100, 999)}"

            # 1. Product
            product = Product.objects.create(
                user=user,
                category=cat,
                name=prod_name,
                has_price=True, # پیش‌فرض را True می‌گیریم
                price=Decimal(random.choice([50000, 100000, 250000])), # قیمت پایه محصول
                price_per_unit=unit_step, # اصلاح شده: تنظیم گام شمارش
                description=f"توضیحات محصول تستی {prod_name} با کیفیت چاپ عالی.",
                is_active=True,
                has_quantity=not is_large_format # اگر لارج فرمت نیست، معمولا تیراژ بسته‌ای دارد
            )

            # 2. Pricing Config
            ProductPricingConfig.objects.create(
                product=product,
                # تنظیمات تیراژ
                allow_custom_quantity=is_large_format, # برای بنر، تیراژ دلخواه (عدد) داریم
                min_quantity=1 if is_large_format else 1000,
                max_quantity=100000,
                
                # تنظیمات ابعاد (اصلاح شده)
                accepts_custom_dimensions=is_large_format,
                min_width=10.0 if is_large_format else 0,
                max_width=500.0 if is_large_format else 0,
                
                # تنظیمات مالی
                base_setup_price=Decimal(50000),
                design_service_available=True,
                design_fee=Decimal(150000)
            )

            # 3. Images (اختیاری)
            # فقط رکورد دیتابیس می‌سازیم، فایل واقعی آپلود نمی‌شود تا سرعت بالا باشد
            # ProductImage.objects.create(...) 

            # 4. Sizes & Quantities (Legacy support / Standard Products)
            if not is_large_format:
                # اتصال ۲ سایز رندوم
                for s in random.sample(sizes, k=2):
                    ProductSize.objects.create(
                        user=user, 
                        product=product, 
                        size=s, 
                        price_impact=Decimal(random.choice([0, 10000]))
                    )
                
                # اتصال همه تیراژها
                for q in quantities:
                    ProductQuantity.objects.create(
                        user=user, 
                        product=product, 
                        quantity=q, 
                        price=random.randint(100000, 5000000) # قیمت کل بسته
                    )

            # 6. OPTIONS (اصلاح شده)
            # انتخاب چند آپشن برای این محصول
            selected_option_keys = random.sample(list(options_map.keys()), k=random.randint(1, 3))
            
            for idx, opt_key in enumerate(selected_option_keys):
                opt_data = options_map[opt_key]
                opt_obj = opt_data['obj']
                possible_values = opt_data['values']

                # الف) ساخت ProductOption (کانفیگ والد)
                # اصلاح: فیلدهای pricing_strategy و base_price از اینجا حذف شدند چون در مدل نبودند
                prod_opt = ProductOption.objects.create(
                    product=product,
                    option=opt_obj,
                    is_required=random.choice([True, False]),
                    order=idx
                    # name, label, input_type به صورت خودکار در save کپی می‌شوند
                )

                # ب) ساخت مقادیر (ProductOptionValue)
                if opt_obj.input_type in ['text', 'number', 'textarea']:
                    # برای اینپوت‌ها مقدار پیش‌فرض نمی‌سازیم
                    pass 
                else:
                    # برای سلکت/رادیو/چک‌باکس
                    for val_idx, val_label in enumerate(possible_values):
                        ProductOptionValue.objects.create(
                            product_option=prod_opt,
                            label=val_label,
                            value=val_label, 
                            
                            # تنظیمات قیمت
                            has_pricing=True,
                            price_impact=Decimal(random.randint(5000, 50000)),
                            
                            # سایر تنظیمات
                            is_default=(val_idx == 0),
                            order=val_idx
                            # اصلاح: quantity_step حذف شد
                            # اصلاح: user حذف شد (ProductOptionValue یوزر ندارد)
                        )

            self.stdout.write(f" + Created: {product.name} (Large Format: {is_large_format})")
