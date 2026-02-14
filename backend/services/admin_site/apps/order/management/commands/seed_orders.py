import random
import uuid
import os
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

# ===== ایمپورت مدل‌ها ===== #
from core.models import (
    Order, OrderItem, OrderItemFile,
    OrderStatus, Address, Province, City
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates 20 REALISTIC CUSTOM ORDERS (Type 2) without creating base data.'

    # ===== داده‌های واقعی صنعت چاپ ===== #
    PRINT_SCENARIOS = [
        {
            "name": "کارت ویزیت لمینت برجسته",
            "specs": {
                "category": "Office",
                "paper": "گلاسه ۳۰۰ گرم",
                "size": "8.5x4.8 cm",
                "print_side": "دو رو",
                "color_mode": "CMYK + 1 Spot Color",
                "coating": "لمینت مات",
                "finishing": ["یووی موضعی برجسته", "گوشه گرد"],
                "quantity": 1000
            },
            "base_price": 850000
        },
        {
            "name": "تراکت تبلیغاتی A5",
            "specs": {
                "category": "Marketing",
                "paper": "تحریر ۸۰ گرم خارجی",
                "size": "A5 (14.8x21 cm)",
                "print_side": "یک رو",
                "color_mode": "CMYK (Full Color)",
                "coating": "بدون روکش",
                "cutting": "برش مستقیم",
                "quantity": 5000
            },
            "base_price": 2400000
        },
        {
            "name": "کاتالوگ صنعتی (منگنه لوپ)",
            "specs": {
                "category": "Booklet",
                "closed_size": "A4",
                "pages": 16,
                "cover_paper": "گلاسه ۲۵۰ گرم + سلفون مات",
                "inner_paper": "گلاسه ۱۳۵ گرم",
                "binding": "منگنه لوپ (Saddle Stitch)",
                "quantity": 500
            },
            "base_price": 12500000
        },
        {
            "name": "بنر استندی 200x90",
            "specs": {
                "category": "Large Format",
                "material": "بنر ۱۳ اونس کره",
                "size": "90x200 cm",
                "print_quality": "اکوسالونت (High Quality)",
                "finishing": ["پانچ ۴ گوشه", "ولد کردن لبه‌ها"],
                "stand_included": True,
                "quantity": 1
            },
            "base_price": 450000
        },
        {
            "name": "جعبه مقوایی دارویی",
            "specs": {
                "category": "Packaging",
                "material": "ایندربرد ۳۰۰ گرم",
                "size": "Custom Die-cut",
                "print_colors": "4 Colors + Pantone 877C (Silver)",
                "coating": "وارنیش واتر",
                "gluing": "چسب بغل",
                "quantity": 10000
            },
            "base_price": 45000000
        },
        {
            "name": "سربرگ اداری A4",
            "specs": {
                "category": "Office",
                "paper": "کتان ۱۲۰ گرم",
                "size": "A4",
                "print_side": "یک رو",
                "colors": "2 رنگ اختصاصی (سازمانی)",
                "finishing": "سرچسب ۵۰ تایی",
                "quantity": 2000
            },
            "base_price": 3200000
        },
        {
            "name": "فاکتور فروش رسمی (۳ نسخه‌ای)",
            "specs": {
                "category": "Office",
                "paper": "NCR (کاربن‌لس) - سفید/صورتی/زرد",
                "size": "A4",
                "binding": "صحافی پرفراژ و منگنه",
                "numbering": "شماره سریال قرمز برجسته",
                "quantity": 50
            },
            "base_price": 1800000
        }
    ]

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('>>> Start seeding 20 Custom Orders...'))

        # 1. دریافت (نه ساخت) کاربر ادمین
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write(self.style.ERROR("کاربر ادمین یافت نشد! لطفا ابتدا سیستم را با seed_users راه اندازی کنید."))
            return

        # 2. اطمینان از وجود آدرس (فقط اگر نباشد می‌سازد)
        address = self.ensure_address(user)

        # 3. دریافت وضعیت‌های موجود (بدون ساخت وضعیت جدید)
        status_pool = self.fetch_existing_statuses()
        if not status_pool:
            self.stdout.write(self.style.ERROR("هیچ وضعیتی (OrderStatus) در سیستم یافت نشد. لطفا ابتدا seed_status را اجرا کنید."))
            return

        # 4. تولید سفارشات
        with transaction.atomic():
            for i in range(1, 21):
                self.create_custom_order(user, address, status_pool, i)

        self.stdout.write(self.style.SUCCESS('✅ Successfully added 20 REALISTIC CUSTOM ORDERS.'))

    def ensure_address(self, user):
        """ دریافت یا ساخت آدرس پیش‌فرض (اصلاح شده بدون فیلدهای اضافه) """
        # تلاش برای یافتن اولین آدرس کاربر
        existing_addr = Address.objects.filter(user=user).first()
        if existing_addr:
            return existing_addr

        # اگر آدرس نداشت، استان و شهر را چک کن
        province, _ = Province.objects.get_or_create(name="تهران", defaults={'slug': 'tehran'})
        city, _ = City.objects.get_or_create(name="تهران", province=province, defaults={'slug': 'tehran-city'})
        
        # ساخت آدرس با فیلدهای صحیح مدل Address
        address = Address.objects.create(
            user=user,
            province=province,
            city=city,
            postal_code="1234567890",
            address="تهران، میدان انقلاب، کارگر شمالی، پلاک تست"
        )
        return address

    def fetch_existing_statuses(self):
        """ 
        دریافت وضعیت‌های موجود از دیتابیس برای استفاده در سفارشات.
        به هیچ عنوان دیتای جدید در جدول وضعیت نمی‌سازد.
        """
        # دریافت نمونه‌ای از انواع مختلف وضعیت برای تنوع
        initial_status = OrderStatus.objects.filter(status_type='initial').first()
        progress_statuses = list(OrderStatus.objects.filter(status_type='progress')[:2])
        approve_status = OrderStatus.objects.filter(status_type='approve').first()

        pool = []
        
        # اولویت با وضعیت‌های آغازین است
        if initial_status:
            pool.extend([initial_status] * 10) # 50% شانس
        
        if progress_statuses:
            pool.extend(progress_statuses * 3) # 30% شانس
            
        if approve_status:
            pool.extend([approve_status] * 2) # باقی شانس
            
        # اگر هیچ فیلتری کار نکرد، همه را بگیر
        if not pool:
            pool = list(OrderStatus.objects.all())

        return pool

    def create_custom_order(self, user, address, status_pool, index):
        """ ساخت سفارش """
        
        scenario = random.choice(self.PRINT_SCENARIOS)
        selected_status = random.choice(status_pool)
        
        # محاسبه قیمت
        base_price = Decimal(scenario["base_price"])
        variance = Decimal(random.uniform(0.95, 1.05))
        final_price = round(base_price * variance, -3)

        order_code = f"CUST-{timezone.now().year}-{random.randint(10000, 99999)}"
        
        # نام گیرنده از پروفایل یا یوزرنیم
        r_name = user.username
        if hasattr(user, 'customer_profile'):
            r_name = f"{user.customer_profile.first_name} {user.customer_profile.last_name}"

        # 1. Order
        order = Order.objects.create(
            user=user,
            order_code=order_code,
            type='2', # سفارش اختصاصی
            current_status=selected_status,
            address=address,
            recipient_name=r_name,
            recipient_phone="09123456789",
            company_name=f"شرکت تست {index}",
            full_address=address.address,
            total_price=final_price,
            base_products_price=final_price,
            # description=f"سفارش اختصاصی - {scenario['name']}"
        )

        # 2. OrderItem (بدون محصول)
        item_json = {
            "is_custom_order": True,
            "specifications": scenario["specs"],
            "admin_logs": [
                f"{timezone.now().strftime('%Y-%m-%d')}: ثبت خودکار توسط سیدر."
            ]
        }
        
        order_item = OrderItem.objects.create(
            order=order,
            product=None, 
            name=scenario['name'],
            quantity=scenario['specs'].get('quantity', 1000),
            price=final_price,
            status='pending',
            items=item_json,
            description=f"توضیحات فنی: {scenario['specs']['category']}",
            admin_note="بررسی دقیق رنگ‌ها الزامی است."
        )

        # 3. OrderItemFile
        file_count = random.randint(1, 2)
        for f_idx in range(file_count):
            file_version = f_idx + 1
            is_latest = (f_idx == file_count - 1)
            fake_filename = f"design_{order_code}_v{file_version}.jpg"
            
            OrderItemFile.objects.create(
                order_item=order_item,
                file=f"orders/designs/seed/{fake_filename}", 
                version=file_version,
                is_latest=is_latest,
                admin_feedback="" if is_latest else "ورژن قدیمی"
            )

        self.stdout.write(f"   + Order {order_code} created. Status: {selected_status.name}")