import os
import random
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from core.models import ProductCategory

# ========================================== #
#  DATA MAP: استاندارد نام‌گذاری و سلسله‌مراتب
# ========================================== #
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
    help = 'Seeds categories with SAFE English slugs, Persian names, and Images from media/pro/'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.HTTP_INFO(">>> شروع عملیات Seed دسته‌بندی‌ها..."))

        User = get_user_model()
        
        # 1. اطمینان از وجود ادمین برای فیلد user
        if not User.objects.filter(is_superuser=True).exists():
             User.objects.create_superuser(password='admin', phone_number='09137555555')
             self.stdout.write(" + ادمین پیش‌فرض ساخته شد.")
        
        admin_user = User.objects.filter(is_superuser=True).first()

        # 2. تنظیمات منبع تصاویر
        # تصاویر باید در مسیر: your_project/media/pro/ باشند
        source_dir = os.path.join(settings.MEDIA_ROOT, 'pro')
        
        available_images = []
        if os.path.exists(source_dir):
            # فقط فایل‌هایی که واقعا وجود دارند را لیست کن
            available_images = [
                f"{i}.jpg" for i in range(1, 9) 
                if os.path.exists(os.path.join(source_dir, f"{i}.jpg"))
            ]
        
        if not available_images:
            self.stdout.write(self.style.ERROR(f"❌ خطای حیاتی: هیچ عکسی (1.jpg تا 8.jpg) در {source_dir} یافت نشد."))
            self.stdout.write(self.style.WARNING("ادامه عملیات بدون انتساب تصویر..."))

        count_created = 0
        count_updated = 0

        # 3. شروع تراکنش اتمیک
        with transaction.atomic():
            for parent_slug, parent_data in PRINTING_CATEGORIES_MAP.items():
                parent_name = parent_data['name']
                children_map = parent_data['children']

                # --- A. ایجاد یا بروزرسانی والد ---
                parent_cat, created = ProductCategory.objects.update_or_create(
                    slug=parent_slug, 
                    defaults={
                        'name': parent_name,
                        'user': admin_user,
                        'description': f'سفارش آنلاین {parent_name} با کیفیت تضمینی و تحویل فوری.',
                        'is_active': True,
                    }
                )

                # انتساب تصویر والد
                if available_images:
                    self._assign_random_image_secure(parent_cat, source_dir, available_images, is_box_only=False)

                if created:
                    count_created += 1
                    self.stdout.write(f" + والد ایجاد شد: {parent_slug}")
                else:
                    count_updated += 1

                # --- B. ایجاد یا بروزرسانی فرزندان ---
                for child_slug, child_name in children_map.items():
                    child_cat, child_created = ProductCategory.objects.update_or_create(
                        slug=child_slug,
                        defaults={
                            'name': child_name,
                            'parent': parent_cat,
                            'user': admin_user,
                            'description': f'چاپ اختصاصی {child_name} با بهترین متریال.',
                            'is_active': True,
                        }
                    )
                    
                    # انتساب تصویر فرزند
                    if available_images:
                        self._assign_random_image_secure(child_cat, source_dir, available_images, is_box_only=True)
                    
                    if child_created:
                        count_created += 1
                    else:
                        count_updated += 1

        self.stdout.write(self.style.SUCCESS(f"\n✅ عملیات با موفقیت پایان یافت."))
        self.stdout.write(f"جدید: {count_created} | بروزرسانی: {count_updated}")

    def _assign_random_image_secure(self, category_obj, source_dir, image_list, is_box_only=False):
        """
        ذخیره عکس تصادفی با متد save=True برای اطمینان از کپی شدن فایل فیزیکی.
        """
        try:
            # ===== 1. مدیریت بنر عریض (Wide Banner) ===== #
            # فقط برای دسته‌های والد و اگر عکس ندارند
            if not is_box_only and not category_obj.banner_wide:
                img_name = random.choice(image_list)
                img_path = os.path.join(source_dir, img_name)
                
                with open(img_path, 'rb') as f:
                    django_file = File(f)
                    # نام‌گذاری رندوم برای جلوگیری از کش شدن یا تکرار
                    new_name = f"wide_{category_obj.slug}_{random.randint(1000,9999)}.jpg"
                    
                    # [CRITICAL FIX]: save=True باعث می‌شود فایل همان لحظه که باز است ذخیره شود
                    category_obj.banner_wide.save(new_name, django_file, save=True)

            # ===== 2. مدیریت بنر مربعی (Box Banner) ===== #
            # برای همه دسته‌ها اگر عکس ندارند
            if not category_obj.banner_box:
                img_name = random.choice(image_list)
                img_path = os.path.join(source_dir, img_name)
                
                with open(img_path, 'rb') as f:
                    django_file = File(f)
                    new_name = f"box_{category_obj.slug}_{random.randint(1000,9999)}.jpg"
                    
                    # [CRITICAL FIX]: ذخیره فوری
                    category_obj.banner_box.save(new_name, django_file, save=True)
                    
        except Exception as e:
            # فقط لاگ کن و برنامه را متوقف نکن
            self.stdout.write(self.style.ERROR(f"خطا در انتساب عکس به {category_obj.slug}: {e}"))