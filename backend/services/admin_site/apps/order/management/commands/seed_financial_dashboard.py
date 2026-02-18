import random
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import User, Order
from apps.order.models import (
    OrderFinancialSheet,
    OrderFinancialReport,
    OrderFinancialItem,
    OrderFinancialCategory
)

class Command(BaseCommand):
    help = 'پاکسازی تست‌های قبل و تولید دیتای تستی مالی توزیع‌شده در 20 روز گذشته'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # ۰. پاکسازی داده‌های تستی قبلی (برای جلوگیری از به هم ریختگی چارت)
        self.stdout.write(self.style.WARNING("در حال پاکسازی داده‌های تستی قبلی..."))
        # به دلیل CASCADE تمام شیت‌ها و گزارش‌های این سفارشات هم پاک می‌شوند
        Order.objects.filter(order_code__startswith="TEST-").delete()

        self.stdout.write(self.style.WARNING("در حال آماده‌سازی کاربران..."))
        
        # ۱. دریافت یا ایجاد کاربران
        warehouse_user, _ = User.objects.get_or_create(username='warehouse', defaults={'first_name': 'کاربر', 'last_name': 'انبار'})
        printer_user, _ = User.objects.get_or_create(username='printer', defaults={'first_name': 'کاربر', 'last_name': 'چاپ'})
        finance_user, _ = User.objects.get_or_create(username='finance', defaults={'first_name': 'مدیر', 'last_name': 'مالی', 'is_staff': True})

        # ۲. ایجاد دسته‌بندی‌های مالی تستی در صورت نبود
        cost_cat1, _ = OrderFinancialCategory.objects.get_or_create(slug='logistics-cost', defaults={'title': 'هزینه ارسال', 'operation_type': 'logistics'})
        cost_cat2, _ = OrderFinancialCategory.objects.get_or_create(slug='print-cost', defaults={'title': 'هزینه چاپ', 'operation_type': 'print'})
        rev_cat, _ = OrderFinancialCategory.objects.get_or_create(slug='sales-rev', defaults={'title': 'درآمد فروش', 'operation_type': 'sales'})

        now = timezone.now()

        # ۳. تولید ۲۰ سفارش که تاریخ ثبتشان در ۲۰ روز گذشته پخش شده است
        self.stdout.write(self.style.WARNING("در حال ایجاد ۲۰ سفارش توزیع‌شده در ۲۰ روز اخیر..."))
        sheets = []
        for i in range(20):
            # i روز قبل
            target_date = now - timedelta(days=i)
            
            order = Order.objects.create(
                order_code=f"TEST-{random.randint(10000, 99999)}", 
                total_price=0
            )
            # آپدیت دستی تاریخ ایجاد سفارش (چون auto_now_add اجازه ست کردن در Create را نمی‌دهد)
            Order.objects.filter(id=order.id).update(created_at=target_date)

            # ایجاد شیت مالی هم‌تاریخ با سفارش
            sheet, _ = OrderFinancialSheet.objects.get_or_create(order=order)
            OrderFinancialSheet.objects.filter(id=sheet.id).update(created_at=target_date)
            sheets.append((sheet, target_date))

        self.stdout.write(self.style.WARNING("در حال ثبت هزینه‌ها و درآمدها برای سفارشات..."))
        
        # ۴. برای هر سفارش، یک گزارش درآمد و یک گزارش هزینه با تاریخ دقیقاً یکسان با سفارش می‌سازیم
        for idx, (sheet, target_date) in enumerate(sheets):
            
            # --- الف) ثبت گزارش هزینه ---
            submitter = random.choice([warehouse_user, printer_user])
            category = cost_cat1 if submitter == warehouse_user else cost_cat2
            
            cost_report = OrderFinancialReport.objects.create(
                sheet=sheet, submitter=submitter, title=f"هزینه سفارش {idx+1}", nature='cost', is_approved=True
            )
            OrderFinancialReport.objects.filter(id=cost_report.id).update(created_at=target_date)
            
            OrderFinancialItem.objects.create(
                report=cost_report, category=category, amount=random.randint(50000, 500000), custom_title=f"هزینه {category.title}"
            )

            # --- ب) ثبت گزارش درآمد ---
            rev_report = OrderFinancialReport.objects.create(
                sheet=sheet, submitter=finance_user, title=f"درآمد سفارش {idx+1}", nature='revenue', is_approved=True
            )
            OrderFinancialReport.objects.filter(id=rev_report.id).update(created_at=target_date)
            
            OrderFinancialItem.objects.create(
                report=rev_report, category=rev_cat, amount=random.randint(200000, 2000000), custom_title="درآمد فاکتور نهایی"
            )

            # --- ج) آپدیت کردن جمع کل Sheetها ---
            sheet.recalculate_totals()

        self.stdout.write(self.style.SUCCESS("✅ تولید دیتای تستی با موفقیت انجام شد!"))
        self.stdout.write(self.style.SUCCESS("دیتاها به درستی در ۲۰ روز اخیر پخش شدند. می‌توانید API داشبورد را بررسی کنید."))
