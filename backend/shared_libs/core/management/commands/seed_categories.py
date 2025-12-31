import os
import random
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from core.models import ProductCategory

# ===== داده‌های استاندارد (Key=Slug, Value=Name) ===== #
PRINTING_CATEGORIES_MAP = {
    "advertising-flyer": {
        "name": "تراکت تبلیغاتی",
        "children": {
            "flyer-80g": "تراکت تحریر ۸۰ گرم",
            "flyer-glossy-135": "تراکت گلاسه ۱۳۵ گرم",
            "flyer-kraft": "تراکت کرافت",
            "flyer-luxury": "تراکت لاکچری"
        }
    },
    "brochure-catalog": {
        "name": "بروشور و کاتالوگ",
        "children": {
            "brochure-2-fold": "بروشور دو لت",
            "brochure-3-fold": "بروشور سه لت",
            "catalog-wire": "کاتالوگ سیمی",
            "catalog-glue": "کاتالوگ چسب گرم"
        }
    },
    "banner-large-format": {
        "name": "بنر و لارج فرمت",
        "children": {
            "banner-13oz": "بنر ایرانی ۱۳ انس",
            "banner-china": "بنر چینی",
            "flex-3m": "فلکس عرض ۳ متر",
            "banner-birthday": "بنر تولد"
        }
    },
    "sticker-mesh": {
        "name": "استیکر و مش",
        "children": {
            "sticker-glass": "استیکر شیشه‌ای",
            "sticker-milky": "استیکر شیری",
            "mesh-adhesive": "مش چسب‌دار",
            "sticker-plotter": "استیکر کاتر پلاتر"
        }
    },
    "office-set": {
        "name": "ست اداری",
        "children": {
            "envelope-a4": "پاکت A4 اداری",
            "envelope-dl": "پاکت ملخی",
            "letterhead-a4": "سربرگ A4",
            "business-card": "کارت ویزیت"
        }
    },
    "packaging": {
        "name": "بسته‌بندی",
        "children": {
            "product-box": "جعبه محصول",
            "hard-box": "هارد باکس",
            "shopping-bag": "ساک دستی"
        }
    }
}

class Command(BaseCommand):
    help = 'Seeds categories with images from media/pro/'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.HTTP_INFO(">>> شروع عملیات ایجاد دسته‌بندی‌ها..."))

        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
             User.objects.create_superuser('admin123', 'admin@printoo.ir', 'admin123')
        
        admin_user = User.objects.filter(is_superuser=True).first()

        # ===== تنظیمات مسیر تصاویر ===== #
        # تصاویر باید در پوشه media/pro باشند (1.jpg تا 8.jpg)
        source_dir = os.path.join(settings.MEDIA_ROOT, 'pro')
        
        # لیست فایل‌های موجود را بررسی می‌کنیم
        available_images = []
        if os.path.exists(source_dir):
            available_images = [f"{i}.jpg" for i in range(1, 9) if os.path.exists(os.path.join(source_dir, f"{i}.jpg"))]
        
        if not available_images:
            self.stdout.write(self.style.WARNING(f"⚠️ هشداری: تصویری در مسیر {source_dir} یافت نشد."))

        count_created = 0
        count_updated = 0

        with transaction.atomic():
            for parent_slug, parent_data in PRINTING_CATEGORIES_MAP.items():
                parent_name = parent_data['name']
                children_map = parent_data['children']

                # --- A. ایجاد والد ---
                parent_cat, created = ProductCategory.objects.update_or_create(
                    slug=parent_slug, 
                    defaults={
                        'name': parent_name,
                        'user': admin_user,
                        'description': f'سفارش آنلاین {parent_name} با کیفیت تضمینی.',
                        'is_active': True,
                    }
                )

                if created and available_images:
                    self._assign_random_image(parent_cat, source_dir, available_images)
                    parent_cat.save()

                if created:
                    count_created += 1
                    self.stdout.write(f" + Parent: {parent_slug}")
                else:
                    count_updated += 1

                # --- B. ایجاد فرزندان ---
                for child_slug, child_name in children_map.items():
                    child_cat, child_created = ProductCategory.objects.update_or_create(
                        slug=child_slug,
                        defaults={
                            'name': child_name,
                            'parent': parent_cat,
                            'user': admin_user,
                            'description': f'چاپ فوری {child_name}',
                            'is_active': True,
                        }
                    )
                    
                    if child_created and available_images:
                        self._assign_random_image(child_cat, source_dir, available_images, is_box_only=True)
                        child_cat.save()
                    
                    if child_created:
                        count_created += 1
                    else:
                        count_updated += 1

        self.stdout.write(self.style.SUCCESS(f"\n✅ عملیات با موفقیت انجام شد."))
        self.stdout.write(f"جدید: {count_created} | بروزرسانی: {count_updated}")

    def _assign_random_image(self, category_obj, source_dir, image_list, is_box_only=False):
        """ذخیره عکس تصادفی برای دسته‌بندی"""
        try:
            # ===== انتخاب عکس برای بنر عریض ===== #
            if not is_box_only and not category_obj.banner_wide:
                img_name = random.choice(image_list)
                img_path = os.path.join(source_dir, img_name)
                with open(img_path, 'rb') as f:
                    django_file = File(f)
                    # نام فایل مقصد را تغییر می‌دهیم تا تکراری نشود
                    new_name = f"wide_{category_obj.slug}_{random.randint(1000,9999)}.jpg"
                    category_obj.banner_wide.save(new_name, django_file, save=False)

            # ===== انتخاب عکس برای بنر باکس ===== #
            if not category_obj.banner_box:
                img_name = random.choice(image_list) # ممکن است با بالایی متفاوت باشد
                img_path = os.path.join(source_dir, img_name)
                with open(img_path, 'rb') as f:
                    django_file = File(f)
                    new_name = f"box_{category_obj.slug}_{random.randint(1000,9999)}.jpg"
                    category_obj.banner_box.save(new_name, django_file, save=False)
                    
        except Exception as e:
            # لاگ کردن خطا در صورت نیاز
            print(f"Error assigning image to category: {e}")
