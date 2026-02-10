from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.db.models.signals import pre_delete
# مسیر ایمپورت را بر اساس پروژه‌ات چک کن (معمولا در core.signals یا apps.home.signals)
try:
    from core.signals import prevent_system_data_deletion
except ImportError:
    # اگر در core نبود، شاید در اپ home باشد
    from apps.home.signals import prevent_system_data_deletion

from core.models import OrderStatus, OrderStatusGroup

class Command(BaseCommand):
    help = 'Replaces Order Statuses with the simplified 6-step workflow'

    def handle(self, *args, **kwargs):
        self.stdout.write("Start seeding Simplified Order Statuses...")

        try:
            with transaction.atomic():
                # 1. قطع موقت سیگنال‌های محافظ (برای رفع ارور 403 موقع حذف)
                self.stdout.write("Disabling protection signals...")
                pre_delete.disconnect(prevent_system_data_deletion, sender=OrderStatus)
                pre_delete.disconnect(prevent_system_data_deletion, sender=OrderStatusGroup)
                
                # 2. پاکسازی کامل جدول
                self._force_clean_table()

                # 3. ریست کردن شمارنده ID (رفع ارور Duplicate Key)
                self._fix_sequence_pointers()

                # 4. ایجاد داده‌های جدید (لیست ۶ تایی)
                self._create_statuses()
                
                # 5. تنظیم نهایی عقربه دیتابیس
                self._fix_sequence_pointers()

                # 6. وصل مجدد سیگنال‌ها
                pre_delete.connect(prevent_system_data_deletion, sender=OrderStatus)
                pre_delete.connect(prevent_system_data_deletion, sender=OrderStatusGroup)

                self.stdout.write(self.style.SUCCESS("Successfully updated Order Statuses to the new 6 items!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding data: {e}"))

    def _force_clean_table(self):
        if OrderStatus.objects.exists():
            self.stdout.write("Deleting existing Statuses...")
            OrderStatus.objects.all().delete()
        
        if OrderStatusGroup.objects.exists():
            self.stdout.write("Deleting existing Groups...")
            OrderStatusGroup.objects.all().delete()

    def _fix_sequence_pointers(self):
        """ریست کردن شمارنده ID برای دیتابیس PostgreSQL"""
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT setval(pg_get_serial_sequence('core_orderstatus', 'id'), 
                    COALESCE((SELECT MAX(id) FROM core_orderstatus), 0) + 1, false);
                """)
                cursor.execute("""
                    SELECT setval(pg_get_serial_sequence('core_orderstatusgroup', 'id'), 
                    COALESCE((SELECT MAX(id) FROM core_orderstatusgroup), 0) + 1, false);
                """)

    def _create_statuses(self):
        # 1. ایجاد یک گروه عمومی (چون مدل Status به Group نیاز دارد)
        general_group = OrderStatusGroup.objects.create(
            name="عمومی",
            code="general",
            description="وضعیت‌های اصلی سفارش",
            is_system=True
        )

        # 2. لیست ۶ تایی مورد نظر شما
        # نکته: internal_code ها برای استفاده در کدنویسی (API) ثابت و انگلیسی هستند
        statuses_data = [
            {
                "id": 1,
                "name": "در انتظار بررسی",
                "internal_code": "PENDING_REVIEW", # معادل Initial
                "status_type": "initial",
                "description": "سفارش ثبت شده و منتظر بررسی ادمین است."
            },
            {
                "id": 2,
                "name": "تایید شده",
                "internal_code": "CONFIRMED",
                "status_type": "approve", # معادل تایید
                "description": "سفارش تایید شد و در صف انجام است."
            },
            {
                "id": 3,
                "name": "آماده ارسال",
                "internal_code": "READY_TO_SHIP",
                "status_type": "progress",
                "description": "سفارش تکمیل و آماده ارسال است."
            },
            {
                "id": 4,
                "name": "ارسال شده",
                "internal_code": "SHIPPED",
                "status_type": "progress",
                "description": "سفارش به پست/پیک تحویل داده شد."
            },
            {
                "id": 5,
                "name": "تحویل شده",
                "internal_code": "DELIVERED",
                "status_type": "approve", # پایان موفق
                "description": "به دست مشتری رسید."
            },
            {
                "id": 6,
                "name": "لغو شده",
                "internal_code": "CANCELED",
                "status_type": "cancel", # پایان ناموفق
                "description": "سفارش لغو شد."
            },
        ]

        status_objects = []
        for s_data in statuses_data:
            status_objects.append(OrderStatus(
                # اگر بخواهیم ID ها دقیقا 1 تا 6 باشند، می‌توانیم اینجا id=s_data['id'] را پاس بدهیم
                # اما چون sequence را ریست کردیم، خودکار 1 تا 6 می‌شوند.
                name=s_data['name'],
                internal_code=s_data['internal_code'],
                status_type=s_data['status_type'],
                group=general_group,
                description=s_data['description'],
                is_system=True, # این باعث می‌شود در ادمین حذف نشوند (محافظت شده)
                sort_order=s_data['id'] # ترتیب نمایش
            ))
        
        OrderStatus.objects.bulk_create(status_objects)