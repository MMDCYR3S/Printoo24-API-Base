import os
import random
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from django.contrib.auth import get_user_model
from core.models import ProductCategory

# ===== لیست داده‌های حرفه‌ای صنعت چاپ ===== #
PRINTING_CATEGORIES = {
    "تراکت تبلیغاتی": ["تراکت تحریر ۸۰ گرم", "تراکت گلاسه ۱۳۵ گرم", "تراکت کرافت"],
    "بروشور و کاتالوگ": ["بروشور دو لت", "بروشور سه لت", "کاتالوگ سیمی"],
    "بنر و لارج فرمت": ["بنر ایرانی ۱۳ انس", "بنر چینی", "فلکس"],
    "استیکر و مش": ["استیکر شیشه‌ای", "استیکر شیری", "مش چسب‌دار"],
    "پاکت نامه": ["پاکت A4", "پاکت A3", "پاکت حباب‌دار"],
    "فاکتور و قبض": ["فاکتور رسمی", "فاکتور کاربن‌لس", "قبض رسید"],
    "لیبل و برچسب": ["لیبل کاغذی", "لیبل پی‌وی‌سی", "لیبل متالایز"],
    "پوستر": ["پوستر گلاسه", "پوستر تحریر", "پوستر دیواری"],
    "فولدر و پوشه": ["فولدر دکمه‌دار", "فولدر مقوایی", "زونکن اختصاصی"],
    "ساک دستی": ["ساک دستی کاغذی", "ساک دستی پارچه‌ای", "ساک دستی نایلونی"],
    "جعبه و بسته‌بندی": ["جعبه مقوایی", "هارد باکس", "کارتن بسته‌بندی"],
    "تقویم و سررسید": ["تقویم رومیزی", "تقویم دیواری", "سررسید وزیری"],
    "هدایای تبلیغاتی": ["خودکار تبلیغاتی", "فلش مموری", "جاسویچی"],
    "ماگ و لیوان": ["ماگ سرامیکی", "لیوان کاغذی", "ماگ حرارتی"],
    "تی‌شرت و لباس": ["تی‌شرت نخ‌پنبه", "کلاه تبلیغاتی", "لباس کار"],
    "مهر و ژلاتین": ["مهر ژلاتینی", "مهر لیزری", "مهر برجسته"],
    "تابلوسازی": ["تابلو چلنیوم", "تابلو لایت باکس", "تابلو پلکسی"],
    "صحافی و جلد": ["صحافی فنر دوبل", "صحافی گالینگور", "صحافی چسب گرم"],
    "چاپ فضای داخلی": ["پلات و لمینت", "تخته شاسی", "فوم برد"],
    "چاپ روی اجسام": ["چاپ روی سنگ", "چاپ روی چوب", "چاپ روی فلز"],
    "سازه نمایشگاهی": ["رول آپ", "پاپ آپ", "میز کانتر"],
    "کارت دعوت": ["کارت عروسی", "کارت تبریک", "کارت دعوت همایش"],
    "منو رستوران": ["منو تک برگ", "منو کتابی", "منو تخته شاسی"],
}

class Command(BaseCommand):
    help = 'Seeds 100 professional printing categories with images'

    def handle(self, *args, **kwargs):
        self.stdout.write("شروع فرآیند ساخت دسته‌بندی‌ها...")

        # 1. پیدا کردن یا ساخت کاربر ادمین (برای فیلد user)
        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.create_superuser('admin_seeder', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.WARNING("کاربر ادمین یافت نشد، یک کاربر موقت ساخته شد."))

        # 2. بررسی وجود عکس‌ها در مسیر media/products/
        source_dir = os.path.join(settings.MEDIA_ROOT, 'pro')
        if not os.path.exists(source_dir):
            self.stdout.write(self.style.ERROR(f"مسیر {source_dir} یافت نشد. لطفاً عکس‌ها را آپلود کنید."))
            return

        available_images = [f"{i}.jpg" for i in range(1, 9)] # 1.jpg تا 8.jpg
        
        count = 0
        
        # 3. حلقه ایجاد دسته‌بندی‌ها
        for parent_name, children in PRINTING_CATEGORIES.items():
            # --- ایجاد دسته‌بندی والد ---
            parent_cat, created = ProductCategory.objects.get_or_create(
                name=parent_name,
                user=user,
                defaults={
                    'description': f'خدمات حرفه‌ای چاپ {parent_name} با کیفیت تضمینی',
                    'is_active': True
                }
            )
            
            # انتساب عکس به والد
            self.assign_image(parent_cat, source_dir, available_images)
            parent_cat.save()
            
            if created:
                count += 1
                self.stdout.write(f"دسته اصلی ایجاد شد: {parent_name}")

            # --- ایجاد زیرمجموعه‌ها (3 تا برای هر کدام) ---
            for child_name in children:
                child_cat, child_created = ProductCategory.objects.get_or_create(
                    name=child_name,
                    user=user,
                    parent=parent_cat,
                    defaults={
                        'description': f'سفارش آنلاین {child_name} با بهترین قیمت',
                        'is_active': True
                    }
                )
                
                # انتساب عکس به فرزند
                self.assign_image(child_cat, source_dir, available_images)
                child_cat.save()

                if child_created:
                    count += 1

        self.stdout.write(self.style.SUCCESS(f"عملیات با موفقیت انجام شد. مجموعاً {count} دسته‌بندی ایجاد شد."))

    def assign_image(self, category_obj, source_dir, image_list):
        """
        یک عکس تصادفی را انتخاب کرده و به فیلدهای بنر اختصاص می‌دهد.
        """
        # انتخاب عکس تصادفی
        selected_img_name = random.choice(image_list)
        img_path = os.path.join(source_dir, selected_img_name)

        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                # استفاده از File جنگو برای ذخیره کپی عکس در مسیر جدید (categories/banners/)
                django_file = File(f)
                
                # اگر عکس ندارد، ست کن (برای جلوگیری از آپلود تکراری در هربار اجرا)
                if not category_obj.banner_wide:
                    category_obj.banner_wide.save(f"wide_{selected_img_name}", django_file, save=False)
                
                if not category_obj.banner_box:
                    # برای باکس هم همان عکس را می‌گذاریم (یا می‌توانید عکس دیگری انتخاب کنید)
                    # نشانگر فایل را به اول برمی‌گردانیم تا دوباره خوانده شود
                    f.seek(0)
                    category_obj.banner_box.save(f"box_{selected_img_name}", django_file, save=False)