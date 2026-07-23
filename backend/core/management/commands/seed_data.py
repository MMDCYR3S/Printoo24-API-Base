from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from core.models import (
    Product, ProductCategory, Material, ProductMaterial, 
    ProductPricingConfig, ProductOption, ProductSize, Size, 
    PricingType, Option, OptionValue, FileUploadSpec, ProductFileUploadRequirement
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds database with test print products including User'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting seeding process...")

        # 1. ساخت یا دریافت کاربر ادمین (صاحب محصولات)
        admin_user, created = User.objects.get_or_create(
            email="admin@printoo24.com",
            defaults={
                'username': 'admin_seeder',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created Admin User: {admin_user.email}"))

        # 2. ساخت دسته‌بندی
        category, _ = ProductCategory.objects.get_or_create(
            slug='digital-offset',
            defaults={
                'user': admin_user,
                'name': "چاپ دیجیتال و افست",
            }
        )

        # 3. ساخت متریال‌های پایه
        glossy_paper, _ = Material.objects.get_or_create(
            price_per_sqm=500000,
            defaults={
                'user': admin_user,
                'name': "کاغذ گلاسه ۳۰۰ گرم",
                'description': "کاغذ گلاسه ضخیم مات"
            }
        )

        banner_material, _ = Material.objects.get_or_create(
            price_per_sqm=150000,
            defaults={
                'user': admin_user,
                'name': "بنر ۱۳ انس",
                'description': "بنر با کیفیت خارجی"
            }
        )

        # 4. ساخت مشخصات آپلود فایل (Upload Specs)
        spec_front, _ = FileUploadSpec.objects.get_or_create(name="طرح رو")
        spec_back, _ = FileUploadSpec.objects.get_or_create(name="طرح پشت")

        # ==========================================
        # محصول ۱: کارت ویزیت (سایز ثابت، تیراژ پکیجی)
        # ==========================================
        vizit_card, created = Product.objects.get_or_create(
            slug='glossy-business-card',
            defaults={
                'user': admin_user,
                'category': category,
                'name': "کارت ویزیت گلاسه",
                'description': 'چاپ کارت ویزیت فوری',
                'has_quantity': True
            }
        )

        if created:
            # کانفیگ
            ProductPricingConfig.objects.create(
                product=vizit_card,
                allow_custom_quantity=False,
                min_quantity=1000,
                max_quantity=10000,
                accepts_custom_dimensions=False,
                base_setup_price=200000,
                design_service_available=True,
                design_fee=150000
            )

            # اتصال متریال
            ProductMaterial.objects.create(
                user=admin_user,
                product=vizit_card,
                material=glossy_paper,
                is_default=True,
                processing_fee_percentage=20
            )

            # سایز
            size_9x5, _ = Size.objects.get_or_create(
                name="9x5", 
                defaults={'user': admin_user, 'width': 9.0, 'height': 5.0}
            )
            ProductSize.objects.create(
                user=admin_user,
                product=vizit_card,
                size=size_9x5
            )

            # آپشن‌ها (ابتدا باید آپشن مادر تعریف شود)
            opt_cellophane, _ = Option.objects.get_or_create(
                name="سلفون", 
                defaults={'user': admin_user, 'code': 'cellophane'}
            )
            val_matte, _ = OptionValue.objects.get_or_create(
                option=opt_cellophane, 
                value="مات", 
                defaults={'user': admin_user}
            )

            # اتصال آپشن به محصول
            ProductOption.objects.create(
                user=admin_user,
                product=vizit_card,
                option=opt_cellophane,
                option_value=val_matte,
                pricing_type=PricingType.PER_SQM,
                price_impact=20000 # 20 تومن هر متر مربع
            )
            
            # نیازهای فایل
            ProductFileUploadRequirement.objects.create(product=vizit_card, spec=spec_front, sort_order=1)
            ProductFileUploadRequirement.objects.create(product=vizit_card, spec=spec_back, sort_order=2)

            self.stdout.write(self.style.SUCCESS(f"Product Created: {vizit_card.name}"))

        # ==========================================
        # محصول ۲: بنر (سایز دلخواه، تیراژ دستی)
        # ==========================================
        banner_prod, created = Product.objects.get_or_create(
            slug='large-format-banner',
            defaults={
                'user': admin_user,
                'category': category,
                'name': "چاپ بنر عریض",
                'description': 'بنر مناسبتی و تبلیغاتی',
                'has_quantity': True
            }
        )

        if created:
            ProductPricingConfig.objects.create(
                product=banner_prod,
                allow_custom_quantity=True,
                min_quantity=1,
                max_quantity=500,
                accepts_custom_dimensions=True,
                min_width=50,
                max_width=320,
                base_setup_price=0,
                design_service_available=True,
                design_fee=100000
            )

            ProductMaterial.objects.create(
                user=admin_user,
                product=banner_prod,
                material=banner_material,
                is_default=True,
                processing_fee_percentage=10
            )
            
            # آپشن پانچ
            opt_punch, _ = Option.objects.get_or_create(
                name="پانچ", 
                defaults={'user': admin_user, 'code': 'punch'}
            )
            val_4corners, _ = OptionValue.objects.get_or_create(
                option=opt_punch, 
                value="۴ گوشه", 
                defaults={'user': admin_user}
            )

            ProductOption.objects.create(
                user=admin_user,
                product=banner_prod,
                option=opt_punch,
                option_value=val_4corners,
                pricing_type=PricingType.PER_UNIT,
                price_impact=5000 # دانه‌ای ۵ هزار تومان
            )
            
            # نیاز فایل (فقط طرح رو)
            ProductFileUploadRequirement.objects.create(product=banner_prod, spec=spec_front, sort_order=1)

            self.stdout.write(self.style.SUCCESS(f"Product Created: {banner_prod.name}"))

        self.stdout.write(self.style.SUCCESS("Seeding completed successfully."))