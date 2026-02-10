from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.db.models.signals import pre_delete
# نکته مهم: مسیر ایمپورت زیر را بر اساس ساختار پروژه‌ات چک کن
# احتمالا در core.signals یا apps.home.signals باشد.
# من فرض کردم در core.signals است طبق کدی که فرستادی.
from core.signals import prevent_system_data_deletion 
from core.models import OrderStatus, OrderStatusGroup

class Command(BaseCommand):
    help = 'Seeds initial Order Statuses safely by temporarily disabling system protection signals'

    def handle(self, *args, **kwargs):
        self.stdout.write("Start seeding Order Statuses...")

        try:
            with transaction.atomic():
                # 1. خاموش کردن موقت سیگنال محافظ
                self.stdout.write("Disabling 'prevent_system_data_deletion' signal...")
                pre_delete.disconnect(prevent_system_data_deletion, sender=OrderStatus)
                pre_delete.disconnect(prevent_system_data_deletion, sender=OrderStatusGroup)
                
                # 2. پاکسازی کامل جدول (حالا که سیگنال خاموش است، واقعا پاک می‌شوند)
                self._force_clean_table()

                # 3. تعمیر عقربه دیتابیس (Sequence) - ریست به 1
                self._fix_sequence_pointers()

                # 4. ایجاد داده‌های جدید
                self._create_statuses()
                
                # 5. تنظیم نهایی عقربه دیتابیس
                self._fix_sequence_pointers()

                # 6. روشن کردن مجدد سیگنال (اختیاری چون اسکریپت تمام می‌شود، ولی برای اصول تمیزکاری)
                pre_delete.connect(prevent_system_data_deletion, sender=OrderStatus)
                pre_delete.connect(prevent_system_data_deletion, sender=OrderStatusGroup)

                self.stdout.write(self.style.SUCCESS("Successfully seeded Order Statuses!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding data: {e}"))

    def _force_clean_table(self):
        """
        حذف داده‌ها با اطمینان، چون سیگنال قطع شده است.
        """
        if OrderStatus.objects.exists():
            count = OrderStatus.objects.count()
            self.stdout.write(f"Deleting {count} existing Statuses...")
            OrderStatus.objects.all().delete()
        
        if OrderStatusGroup.objects.exists():
            count = OrderStatusGroup.objects.count()
            self.stdout.write(f"Deleting {count} existing Groups...")
            OrderStatusGroup.objects.all().delete()

    def _fix_sequence_pointers(self):
        """
        ریست کردن شمارنده ID دیتابیس پستگرس.
        """
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                # فرمول: Max(id) + 1. اگر جدول خالی باشد (که الان هست)، می‌شود 1.
                cursor.execute("""
                    SELECT setval(pg_get_serial_sequence('core_orderstatus', 'id'), 
                    COALESCE((SELECT MAX(id) FROM core_orderstatus), 0) + 1, false);
                """)
                cursor.execute("""
                    SELECT setval(pg_get_serial_sequence('core_orderstatusgroup', 'id'), 
                    COALESCE((SELECT MAX(id) FROM core_orderstatusgroup), 0) + 1, false);
                """)

    def _create_statuses(self):
        # تعریف گروه‌ها
        groups_data = [
            {"name": "واحد مالی و اداری", "code": "accounting", "description": "بررسی وضعیت پرداخت و تاییدیه اولیه"},
            {"name": "واحد لیتوگرافی و طراحی", "code": "prepress", "description": "بررسی فنی فایل‌های چاپی"},
            {"name": "واحد تولید و چاپ", "code": "production", "description": "فرآیند چاپ، برش و صحافی"},
            {"name": "واحد انبار و لجستیک", "code": "logistics", "description": "بسته‌بندی و ارسال"},
            {"name": "سیستم", "code": "system", "description": "وضعیت‌های سیستمی"},
        ]

        groups_map = {}
        for g_data in groups_data:
            group = OrderStatusGroup.objects.create(
                code=g_data['code'],
                name=g_data['name'],
                description=g_data['description'],
                is_system=True
            )
            groups_map[g_data['code']] = group

        # تعریف وضعیت‌ها
        statuses_data = [
            {"name": "در انتظار پرداخت", "internal_code": "PENDING_PAYMENT", "status_type": "initial", "group": "accounting", "description": "سفارش ثبت شده اما پرداخت نشده است."},
            {"name": "پرداخت شده (در انتظار بررسی)", "internal_code": "PAYMENT_VERIFIED", "status_type": "progress", "group": "accounting", "description": "تراکنش موفق بوده، منتظر بررسی فایل."},
            {"name": "در حال بررسی فایل", "internal_code": "CHECKING_FILE", "status_type": "progress", "group": "prepress", "description": "اپراتور در حال چک کردن کیفیت فایل است."},
            {"name": "رد شده (نقص فایل)", "internal_code": "FILE_REJECTED", "status_type": "reject", "group": "prepress", "description": "فایل مشکل دارد."},
            {"name": "تایید شده (ارسال به چاپ)", "internal_code": "FILE_APPROVED", "status_type": "approve", "group": "prepress", "description": "فایل تایید و فرم‌بندی شد."},
            {"name": "در حال چاپ", "internal_code": "PRINTING_PROCESS", "status_type": "progress", "group": "production", "description": "در پروسه چاپ."},
            {"name": "خدمات تکمیلی (برش/صحافی)", "internal_code": "POST_PRESS", "status_type": "progress", "group": "production", "description": "مراحل پس از چاپ."},
            {"name": "آماده ارسال", "internal_code": "READY_TO_SHIP", "status_type": "progress", "group": "logistics", "description": "بسته‌بندی شده."},
            {"name": "ارسال شده", "internal_code": "SHIPPED", "status_type": "progress", "group": "logistics", "description": "تحویل پست شد."},
            {"name": "تحویل شده", "internal_code": "DELIVERED", "status_type": "approve", "group": "logistics", "description": "به دست مشتری رسید."},
            {"name": "لغو شده", "internal_code": "CANCELED", "status_type": "cancel", "group": "system", "description": "لغو سیستمی."},
        ]

        # چون جدول را پاک کردیم، اینجا مستقیم create می‌کنیم (سریع‌تر از update_or_create)
        status_objects = []
        for index, s_data in enumerate(statuses_data):
            status_objects.append(OrderStatus(
                internal_code=s_data['internal_code'],
                name=s_data['name'],
                status_type=s_data['status_type'],
                group=groups_map[s_data['group']],
                description=s_data['description'],
                is_system=True,
                sort_order=index + 1
            ))
        OrderStatus.objects.bulk_create(status_objects)