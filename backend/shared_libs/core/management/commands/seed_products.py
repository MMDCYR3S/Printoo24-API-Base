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

            # 3. ساخت سایزهای استاندارد (USER اضافه شد)
            sizes = self.create_master_sizes(admin_user) 
            
            # 5. ساخت آپشن‌ها (USER اضافه شد)
            options_dict = self.create_master_options(admin_user)
            
            # 6. ساخت تیراژها (USER اضافه شد)
            quantities = self.create_master_quantities(admin_user)
            


            # 8. ساخت محصولات اصلی
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
            user = User.objects.create_superuser('admin_seeder', 'admin@seed.com', 'admin123')
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
            # اینجا user را به defaults اضافه کردیم
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
                }
            )
            
            # اگر برای OptionValue هم در مدل User گذاشتی، اینجا هم باید اضافه کنی:
            # for val in values:
            #     OptionValue.objects.get_or_create(..., defaults={'user': user})

            result_map[name] = {'obj': opt, 'values': values}
            
        return result_map

    def create_master_quantities(self, user):
        values = [1000, 2000, 5000, 10000]
        objs = []
        for v in values:
            q, _ = Quantity.objects.get_or_create(
                value=v,
                defaults={'user': user} # <--- اضافه شد
            )
            objs.append(q)
        return objs


    # ==========================================
    # CORE PRODUCT CREATION
    # ==========================================

    def create_products(self, user, categories, sizes, options_map, quantities):
        
        product_bases = [
            ('کارت ویزیت لاکچری', False), ('تراکت تبلیغاتی', False), 
            ('بنر مناسبتی', True), ('استیکر شیشه‌ای', True), 
            ('سربرگ اداری', False), ('پاکت نامه ملخی', False)
        ]

        # عکس‌های تستی (مطمئن شو در مدیا هستند)
        image_pool = [f'pro/{i}.jpg' for i in range(1, 8)]

        for i in range(1, 31):
            base_name, is_large_format = random.choice(product_bases)
            cat = random.choice(categories)
            prod_name = f"{base_name} - کد {random.randint(1000, 9999)}"

            # 1. Product
            product = Product.objects.create(
                user=user,
                category=cat, # کاربر حذف شد (طبق مدل جدید)
                name=prod_name,
                price=Decimal(random.choice([0, 50000, 100000])), # قیمت پایه (مثلا هزینه برش)
                description=f"محصول تستی شماره {i} با کیفیت تضمینی.",
                is_active=True
            )

            # 2. Pricing Config
            ProductPricingConfig.objects.create(
                product=product,
                allow_custom_quantity=is_large_format,
                min_quantity=1 if is_large_format else 1000,
                max_quantity=100000,
                accepts_custom_dimensions=is_large_format,
                base_setup_price=Decimal(50000),
                design_service_available=True,
                design_fee=Decimal(150000)
            )

            # 3. Images
            selected_imgs = random.sample(image_pool, k=random.randint(1, 3))
            for idx, img_path in enumerate(selected_imgs):
                ProductImage.objects.create(
                    user=user,
                    product=product, image=img_path, order=idx
                )

            # 4. Sizes & Quantities (Legacy support)
            # حتی در سیستم جدید، این‌ها برای محصولات استاندارد استفاده می‌شوند
            if not is_large_format:
                for s in random.sample(sizes, k=2):
                    ProductSize.objects.create(user=user, product=product, size=s, price_impact=0)
                
                for q in quantities:
                    ProductQuantity.objects.create(user=user, product=product, quantity=q, price=0)

            # 6. OPTIONS (The New Complex Part)
            # انتخاب چند آپشن برای این محصول
            selected_option_keys = random.sample(list(options_map.keys()), k=2)
            
            for opt_key in selected_option_keys:
                opt_data = options_map[opt_key]
                opt_obj = opt_data['obj']
                possible_values = opt_data['values']

                # الف) ساخت ProductOption (کانفیگ والد)
                # استراتژی قیمت را تصادفی انتخاب می‌کنیم تا تست کامل شود
                strategy = random.choice([
                    OptionPricingStrategy.FIXED, 
                    OptionPricingStrategy.PERCENTAGE,
                    OptionPricingStrategy.PER_SQM if is_large_format else OptionPricingStrategy.FIXED
                ])

                prod_opt = ProductOption.objects.create(
                    product=product,
                    option=opt_obj,
                    is_required=random.choice([True, False]),
                    has_pricing=True,
                    pricing_strategy=strategy,
                    base_price=Decimal(random.choice([0, 10000]))
                )

                # ب) ساخت مقادیر (ProductOptionValue)
                # اگر آپشن متنی یا عددی باشد، مقدار پیش‌فرض ندارد
                if opt_obj.input_type in ['text', 'number', 'textarea']:
                    # برای اینپوت‌ها معمولا یک ولیو دامی یا خالی می‌سازیم اگر نیاز به قیمت باشد
                    pass 
                else:
                    # برای سلکت/رادیو
                    for val_label in possible_values:
                        ProductOptionValue.objects.create(
                            product_option=prod_opt,
                            label=val_label,
                            value=val_label, # در سناریوی واقعی می‌تواند کد باشد
                            price_impact=Decimal(random.randint(5000, 50000)),
                            quantity_step=1 if is_large_format else 1000, # پله‌ای برای کارت ویزیت
                            is_default=False
                        )

            self.stdout.write(f" + Created: {product.name} (Large Format: {is_large_format})")
