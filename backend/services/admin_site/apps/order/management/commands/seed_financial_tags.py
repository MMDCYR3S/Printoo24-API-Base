from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.order.models import OrderFinancialType

class Command(BaseCommand):
    help = 'Populates the database with initial financial tags for the printing industry.'

    def handle(self, *args, **options):
        # لیست تگ‌های تخصصی صنعت چاپ
        financial_tags = [
            # ===== ردیف‌های درآمدی اصلی =====
            {
                "title": "خدمات چاپ",
                "slug": "printing-service",
                "desc": "هزینه مربوط به فرآیند چاپ (افست، دیجیتال، لارج فرمت)"
            },
            {
                "title": "خدمات طراحی",
                "slug": "design-fee",
                "desc": "هزینه طراحی گرافیک و آماده‌سازی فایل"
            },
            {
                "title": "تعرفه فوریت",
                "slug": "urgent-fee",
                "desc": "هزینه اضافه بابت تحویل فوری سفارش"
            },
            
            # ===== خدمات پس از چاپ (Finishing) =====
            {
                "title": "خدمات تکمیلی / صحافی",
                "slug": "finishing-binding",
                "desc": "شامل منگنه، چسب گرم، فنر، جلدسازی"
            },
            {
                "title": "خدمات برش و دایکات",
                "slug": "cutting-diecut",
                "desc": "برش دورگرد، دایکات، نیم‌تیغ"
            },
            {
                "title": "روکش و لمینت",
                "slug": "laminating",
                "desc": "سلفون (مات/براق)، لمینت سرد و گرم، UV"
            },
            {
                "title": "خدمات نصب",
                "slug": "installation-fee",
                "desc": "هزینه اعزام نصاب و نصب (برای استیکر، مش، تابلو)"
            },

            # ===== هزینه‌های متریال (در صورت تفکیک) =====
            {
                "title": "هزینه متریال/کاغذ",
                "slug": "material-cost",
                "desc": "هزینه خام کاغذ، بنر، وینیل و..."
            },
            {
                "title": "هزینه ساخت کلیشه/قالب",
                "slug": "mold-plate-cost",
                "desc": "هزینه ساخت کلیشه، شابلون یا قالب دایکات"
            },

            # ===== لجستیک =====
            {
                "title": "هزینه ارسال / باربری",
                "slug": "shipping-cost",
                "desc": "هزینه پیک، تیپاکس یا باربری"
            },
            {
                "title": "بسته‌بندی",
                "slug": "packaging-fee",
                "desc": "هزینه کارتن، شرینک و بسته‌بندی ایمن"
            },

            # ===== تعدیلات مالی =====
            {
                "title": "مالیات بر ارزش افزوده",
                "slug": "vat",
                "desc": "9% ارزش افزوده"
            },
            {
                "title": "تخفیف ویژه",
                "slug": "special-discount",
                "desc": "کسورات مربوط به تخفیفات"
            },
            {
                "title": "استرداد وجه",
                "slug": "refund",
                "desc": "مبالغ عودت داده شده به مشتری"
            },
            {
                "title": "بیعانه / پیش‌پرداخت",
                "slug": "deposit",
                "desc": "مبالغ دریافتی اولیه"
            },
             {
                "title": "متفرقه",
                "slug": "miscellaneous",
                "desc": "سایر هزینه‌ها"
            },
        ]

        self.stdout.write("شروع ایجاد تگ‌های مالی صنعت چاپ...")

        counter = 0
        for data in financial_tags:
            # استفاده از get_or_create برای جلوگیری از تکرار
            obj, created = OrderFinancialType.objects.get_or_create(
                slug=data['slug'],
                defaults={'title': data['title']}
            )
            
            if created:
                counter += 1
                self.stdout.write(self.style.SUCCESS(f"تگ ایجاد شد: {data['title']}"))
            else:
                # اگر تایتل عوض شده بود آپدیت کن (اختیاری)
                if obj.title != data['title']:
                    obj.title = data['title']
                    obj.save()
                    self.stdout.write(self.style.WARNING(f"تگ بروزرسانی شد: {data['title']}"))

        self.stdout.write(self.style.SUCCESS(f"\nتکمیل شد! تعداد {counter} تگ جدید اضافه گردید."))
