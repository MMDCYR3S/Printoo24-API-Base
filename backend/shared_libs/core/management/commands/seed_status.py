from django.core.management.base import BaseCommand
from django.db import transaction, connection
from core.models import OrderStatus, OrderStatusGroup

class Command(BaseCommand):
    help = 'Seeds Order Statuses with proper grouping'

    def handle(self, *args, **kwargs):
        self.stdout.write("Start seeding Order Statuses...")

        try:
            with transaction.atomic():
                # پاکسازی کامل جدول
                self._force_clean_table()

                # تعمیر sequence
                self._fix_sequence_pointers()

                # ایجاد داده‌های جدید
                self._create_statuses()
                
                # تنظیم نهایی sequence
                self._fix_sequence_pointers()

                self.stdout.write(self.style.SUCCESS("Successfully seeded Order Statuses!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding data: {e}"))

    def _force_clean_table(self):
        if OrderStatus.objects.exists():
            count = OrderStatus.objects.count()
            self.stdout.write(f"Deleting {count} existing Statuses...")
            OrderStatus.objects.all().delete()
        
        if OrderStatusGroup.objects.exists():
            count = OrderStatusGroup.objects.count()
            self.stdout.write(f"Deleting {count} existing Groups...")
            OrderStatusGroup.objects.all().delete()

    def _fix_sequence_pointers(self):
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
        # تعریف گروه‌ها
        groups_data = [
            {"name": "ادمین", "code": "admin", "description": "مدیریت کل سیستم"},
            {"name": "طراح", "code": "designer", "description": "واحد طراحی و لیتوگرافی"},
            {"name": "چاپ", "code": "printing", "description": "واحد تولید و چاپ"},
            {"name": "انبار", "code": "warehouse", "description": "واحد انبار و ارسال"},
            {"name": "مشتری", "code": "customer", "description": "نمایش برای مشتری"},
        ]

        groups_map = {}
        for g_data in groups_data:
            group = OrderStatusGroup.objects.create(
                code=g_data['code'],
                name=g_data['name'],
                description=g_data['description'],
                is_system=False  # حذف کردم is_system رو
            )
            groups_map[g_data['code']] = group

        # تعریف وضعیت‌ها
        statuses_data = [
            {
                "name": "در انتظار بررسی",
                "internal_code": "PENDING_REVIEW",
                "status_type": "initial",
                "group": "admin",  # فقط ادمین
                "description": "سفارش ثبت شده و در انتظار بررسی اولیه",
                "visible_to_customer": True
            },
            {
                "name": "در حال طراحی",
                "internal_code": "DESIGNING",
                "status_type": "progress",
                "group": "designer",  # فقط طراح
                "description": "در حال طراحی و آماده‌سازی فایل چاپ",
                "visible_to_customer": True
            },
            {
                "name": "در حال چاپ",
                "internal_code": "PRINTING",
                "status_type": "progress",
                "group": "printing",  # فقط واحد چاپ
                "description": "در حال پروسه چاپ",
                "visible_to_customer": True
            },
            {
                "name": "ارسال‌شده",
                "internal_code": "SHIPPED",
                "status_type": "progress",
                "group": "warehouse",  # فقط انبار
                "description": "سفارش ارسال شده است",
                "visible_to_customer": True
            },
            {
                "name": "تحویل‌شده",
                "internal_code": "DELIVERED",
                "status_type": "approve",
                "group": "admin",  # فقط ادمین
                "description": "سفارش به دست مشتری رسیده",
                "visible_to_customer": True
            },
            {
                "name": "لغو شده",
                "internal_code": "CANCELED",
                "status_type": "cancel",
                "group": "admin",  # فقط ادمین می‌تونه تغییر بده
                "description": "سفارش لغو شده",
                "visible_to_customer": True
            },
        ]

        status_objects = []
        for index, s_data in enumerate(statuses_data):
            status_objects.append(OrderStatus(
                internal_code=s_data['internal_code'],
                name=s_data['name'],
                status_type=s_data['status_type'],
                group=groups_map[s_data['group']],
                description=s_data['description'],
                is_system=False,  # حذف کردم is_system رو
                sort_order=index + 1
            ))
        OrderStatus.objects.bulk_create(status_objects)
        
        self.stdout.write(self.style.SUCCESS(f"Created {len(status_objects)} statuses in {len(groups_map)} groups"))