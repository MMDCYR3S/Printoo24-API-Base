import os
import random
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from core.models import ProductCategory

# ===== لیست داده‌های حرفه‌ای صنعت چاپ ===== #
PRINTING_CATEGORIES = {
    "تراکت تبلیغاتی": ["تراکت تحریر ۸۰ گرم", "تراکت گلاسه ۱۳۵ گرم", "تراکت کرافت", "تراکت لاکچری"],
    "بروشور و کاتالوگ": ["بروشور دو لت", "بروشور سه لت", "کاتالوگ سیمی", "کاتالوگ چسب گرم"],
    "بنر و لارج فرمت": ["بنر ایرانی ۱۳ انس", "بنر چینی", "فلکس عرض ۳ متر", "بنر تولد"],
    "استیکر و مش": ["استیکر شیشه‌ای", "استیکر شیری", "مش چسب‌دار", "استیکر کاتر پلاتر"],
    "پاکت نامه": ["پاکت A4 اداری", "پاکت ملخی", "پاکت حباب‌دار پستی"],
    "فاکتور و قبض": ["فاکتور رسمی دارایی", "فاکتور کاربن‌لس", "قبض رسید دسته چکی"],
    "لیبل و برچسب": ["لیبل کاغذی (شیت)", "لیبل پی‌وی‌سی (ضد آب)", "لیبل متالایز", "لیبل اموال"],
    "پوستر": ["پوستر گلاسه ۱۳۵", "پوستر مقوایی ۳۰۰ گرم", "پوستر دیواری"],
    "فولدر و پوشه": ["فولدر دکمه‌دار پلاستیکی", "فولدر مقوایی اختصاصی", "زونکن اداری"],
    "ساک دستی": ["ساک دستی گلاسه", "ساک دستی کرافت", "ساک پارچه‌ای سوزنی"],
    "جعبه و بسته‌بندی": ["جعبه مقوایی محصول", "هارد باکس کادویی", "کارتن لمینتی"],
    "تقویم و سررسید": ["تقویم رومیزی پایه سخت", "تقویم دیواری", "سررسید وزیری چرم"],
    "هدایای تبلیغاتی": ["خودکار پلاستیکی", "خودکار فلزی", "فلش مموری", "جاسویچی"],
    "ماگ و لیوان": ["ماگ سرامیکی سفید", "لیوان کاغذی تبلیغاتی", "ماگ حرارتی (جادویی)"],
    "مهر و ژلاتین": ["مهر ژلاتینی فوری", "مهر لیزری اتوماتیک", "مهر برجسته فلزی"],
    "تابلوسازی": ["تابلو چلنیوم", "تابلو لایت باکس", "تابلو پلکسی گلاس"],
    "صحافی و جلد": ["صحافی فنر دوبل", "صحافی گالینگور پایان‌نامه", "صحافی چسب گرم"],
    "چاپ فضای داخلی": ["پلات و لمینت مات", "پلات و لمینت براق", "تخته شاسی ۳۰ در ۴۰"],
    "کارت دعوت": ["کارت عروسی فانتزی", "کارت دعوت همایش", "کارت پستال"],
    "منو رستوران": ["منو تک برگ لمینت", "منو کتابی چرمی", "منو تخته شاسی"],
}

class Command(BaseCommand):
    help = 'Seeds professional printing categories compatible with the new architecture'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.HTTP_INFO(">>> شروع عملیات سیدینگ دسته‌بندی‌ها..."))

        # 1. مدیریت کاربر ادمین (طبق مدل جدید user=ForeignKey)
        User = get_user_model()
        admin_user = User.objects.filter(is_superuser=True).first()
        
        if not admin_user:
            self.stdout.write(self.style.WARNING("کاربر ادمین یافت نشد. در حال ساخت کاربر موقت (admin@seed.com)..."))
            admin_user = User.objects.create_superuser('admin_seeder', 'admin@seed.com', 'admin123')

        # 2. تنظیم مسیر عکس‌ها
        # فرض: عکس‌ها را در مسیر media/seeds/categories ریخته‌اید
        source_dir = os.path.join(settings.MEDIA_ROOT, 'pro')
        
        if not os.path.exists(source_dir):
            os.makedirs(source_dir, exist_ok=True)
            self.stdout.write(self.style.ERROR(
                f"خطا: مسیر {source_dir} خالی است.\n"
                f"لطفاً چند عکس (1.jpg تا 8.jpg) در این پوشه قرار دهید و دوباره تلاش کنید."
            ))
            return

        available_images = [f for f in os.listdir(source_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
        if not available_images:
            self.stdout.write(self.style.ERROR("هیچ عکسی در پوشه seeds پیدا نشد."))
            return

        count_created = 0
        count_updated = 0

        # 3. اجرای تراکنش اتمیک (برای امنیت داده)
        with transaction.atomic():
            for parent_name, children in PRINTING_CATEGORIES.items():
                
                # --- A. ایجاد/آپدیت والد ---
                parent_cat, created = ProductCategory.objects.get_or_create(
                    name=parent_name,
                    defaults={
                        'user': admin_user,
                        'description': f'مرجع تخصصی سفارش آنلاین {parent_name} با ضمانت کیفیت و تحویل فوری.',
                        'is_active': True,
                    }
                )

                # اگر قبلاً بوده اما یوزر نداشته (برای دیتابیس‌های قدیمی) آپدیت کن
                if not created and not parent_cat.user:
                    parent_cat.user = admin_user
                    parent_cat.save()

                # انتساب تصویر به والد (اگر ندارد)
                if not parent_cat.banner_wide or not parent_cat.banner_box:
                    self._assign_random_image(parent_cat, source_dir, available_images)
                    parent_cat.save()

                if created:
                    self.stdout.write(f" + دسته اصلی: {parent_name}")
                    count_created += 1
                else:
                    count_updated += 1

                # --- B. ایجاد/آپدیت فرزندان ---
                for child_name in children:
                    child_cat, child_created = ProductCategory.objects.get_or_create(
                        name=child_name,
                        parent=parent_cat, # اتصال MPTT
                        defaults={
                            'user': admin_user,
                            'description': f'چاپ {child_name} با بهترین متریال موجود در بازار.',
                            'is_active': True,
                        }
                    )

                    # انتساب تصویر به فرزند
                    if not child_cat.banner_box:
                        self._assign_random_image(child_cat, source_dir, available_images, is_box_only=True)
                        child_cat.save()

                    if child_created:
                        count_created += 1
                    else:
                        count_updated += 1

        # 4. گزارش نهایی
        self.stdout.write(self.style.SUCCESS(f"\n✅ پایان عملیات."))
        self.stdout.write(f"مجموع رکوردهای جدید: {count_created}")
        self.stdout.write(f"مجموع رکوردهای بررسی شده: {count_updated}")

    def _assign_random_image(self, category_obj, source_dir, image_list, is_box_only=False):
        """
        انتخاب و ذخیره عکس تصادفی برای بنرها.
        """
        try:
            selected_img_name = random.choice(image_list)
            img_path = os.path.join(source_dir, selected_img_name)

            with open(img_path, 'rb') as f:
                django_file = File(f)
                
                # برای دسته والد، هم بنر عریض میخواهیم هم باکس
                if not is_box_only and not category_obj.banner_wide:
                    # نام فایل را رندوم میکنیم تا تکراری نشود
                    new_name = f"wide_{random.randint(1000,9999)}_{selected_img_name}"
                    category_obj.banner_wide.save(new_name, django_file, save=False)

                # برای همه دسته‌ها بنر مربعی لازم است
                if not category_obj.banner_box:
                    f.seek(0) # برگشت به ابتدای فایل برای خواندن مجدد
                    new_name = f"box_{random.randint(1000,9999)}_{selected_img_name}"
                    category_obj.banner_box.save(new_name, django_file, save=False)
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"خطا در ذخیره عکس برای {category_obj.name}: {e}"))
            
