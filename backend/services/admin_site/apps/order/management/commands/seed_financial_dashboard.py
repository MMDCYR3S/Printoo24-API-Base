import random
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    User,
    Order,
    OrderStatus,
    OrderStateLog,
)
from apps.order.models import (
    OrderFinancialSheet,
    OrderFinancialReport,
    OrderFinancialItem,
    OrderFinancialCategory
)

class Command(BaseCommand):
    help = 'پاکسازی تست‌های قبل و تولید دیتای تستی با وضعیت‌های داینامیک'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # ۰. پاکسازی داده‌های تستی قبلی
        self.stdout.write(self.style.WARNING("در حال پاکسازی داده‌های تستی قبلی..."))
        Order.objects.filter(order_code__startswith="TEST-").delete()

        # ۱. دریافت کاربران و دسته‌بندی‌ها (فرض بر این است که وجود دارند یا ایجاد می‌شوند)
        warehouse_user, _ = User.objects.get_or_create(username='warehouse', defaults={'first_name': 'کاربر', 'last_name': 'انبار'})
        printer_user, _ = User.objects.get_or_create(username='printer', defaults={'first_name': 'کاربر', 'last_name': 'چاپ'})
        finance_user, _ = User.objects.get_or_create(username='finance', defaults={'first_name': 'مدیر', 'last_name': 'مالی', 'is_staff': True})

        cost_cat1, _ = OrderFinancialCategory.objects.get_or_create(slug='logistics-cost', defaults={'title': 'هزینه ارسال', 'operation_type': 'logistics'})
        cost_cat2, _ = OrderFinancialCategory.objects.get_or_create(slug='print-cost', defaults={'title': 'هزینه چاپ', 'operation_type': 'print'})
        rev_cat, _ = OrderFinancialCategory.objects.get_or_create(slug='sales-rev', defaults={'title': 'درآمد فروش', 'operation_type': 'sales'})

        # ۲. واکشی وضعیت‌ها بر اساس sort_order (بدون ایجاد وضعیت جدید)
        # وضعیت‌هایی که ترتیب آن‌ها بین ۱ تا ۵ تنظیم شده را می‌گیریم
        available_statuses = list(OrderStatus.objects.filter(sort_order__range=(1, 5)).order_by('sort_order'))

        if not available_statuses:
            self.stdout.write(self.style.ERROR("خطا: هیچ وضعیتی با sort_order بین 1 تا 5 یافت نشد!"))
            return

        now = timezone.now()

        # ۳. تولید ۲۰ سفارش
        self.stdout.write(self.style.WARNING(f"در حال ایجاد ۲۰ سفارش با استفاده از {len(available_statuses)} وضعیت موجود..."))
        sheets = []
        
        for i in range(20):
            target_date = now - timedelta(days=i)
            
            # انتخاب تصادفی یکی از وضعیت‌های موجود
            selected_status = random.choice(available_statuses)

            order = Order.objects.create(
                order_code=f"TEST-{random.randint(10000, 99999)}", 
                total_price=0,
                current_status=selected_status,
                type="2" # سفارش اختصاصی طبق مدل شما
            )
            
            # اصلاح تاریخ ایجاد
            Order.objects.filter(id=order.id).update(created_at=target_date)

            # ثبت لاگ تغییر وضعیت برای دیتای واقعی‌تر
            OrderStateLog.objects.create(
                order=order,
                from_status=None,
                to_status=selected_status,
                actor=finance_user,
                description="ایجاد خودکار سفارش در مرحله تست"
            )

            # ایجاد شیت مالی
            sheet, _ = OrderFinancialSheet.objects.get_or_create(order=order)
            OrderFinancialSheet.objects.filter(id=sheet.id).update(created_at=target_date)
            sheets.append((sheet, target_date))

        # ۴. ثبت تراکنش‌های مالی برای هر شیت
        self.stdout.write(self.style.WARNING("در حال ثبت هزینه‌ها و درآمدها..."))
        for idx, (sheet, target_date) in enumerate(sheets):
            
            # ثبت هزینه
            submitter = random.choice([warehouse_user, printer_user])
            category = cost_cat1 if submitter == warehouse_user else cost_cat2
            
            cost_report = OrderFinancialReport.objects.create(
                sheet=sheet, submitter=submitter, title=f"هزینه تست {idx+1}", nature='cost', is_approved=True
            )
            OrderFinancialReport.objects.filter(id=cost_report.id).update(created_at=target_date)
            
            OrderFinancialItem.objects.create(
                report=cost_report, category=category, amount=random.randint(50000, 500000), custom_title=f"هزینه {category.title}"
            )

            # ثبت درآمد
            rev_report = OrderFinancialReport.objects.create(
                sheet=sheet, submitter=finance_user, title=f"درآمد تست {idx+1}", nature='revenue', is_approved=True
            )
            OrderFinancialReport.objects.filter(id=rev_report.id).update(created_at=target_date)
            
            OrderFinancialItem.objects.create(
                report=rev_report, category=rev_cat, amount=random.randint(200000, 2000000), custom_title="فروش تستی"
            )

            # بروزرسانی جمع کل
            sheet.recalculate_totals()

        self.stdout.write(self.style.SUCCESS(f"✅ با موفقیت ۲۰ سفارش با وضعیت‌های متنوع (Sort 1-5) ایجاد شد."))
