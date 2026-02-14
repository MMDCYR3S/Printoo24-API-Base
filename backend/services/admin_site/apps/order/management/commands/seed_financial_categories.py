from django.core.management.base import BaseCommand
from apps.order.models import OrderFinancialCategory

class Command(BaseCommand):
    help = 'Seed Financial Categories for Printing Industry'

    def handle(self, *args, **kwargs):
        # ===== REVENUE CATEGORIES (درآمدها) ===== #
        # nature='revenue'
        revenues = [
            # عملیات چاپ (فروش اصلی)
            {'title': 'فروش چاپ افست', 'slug': 'rev-offset', 'op_type': 'sales'},
            {'title': 'فروش چاپ دیجیتال', 'slug': 'rev-digital', 'op_type': 'sales'},
            {'title': 'فروش لارج فرمت (بنر/فلکس)', 'slug': 'rev-large-format', 'op_type': 'sales'},
            
            # خدمات طراحی
            {'title': 'هزینه طراحی گرافیک', 'slug': 'rev-design', 'op_type': 'design'},
            {'title': 'هزینه لیتوگرافی (زینک خروجی)', 'slug': 'rev-lithography', 'op_type': 'design'},
            
            # خدمات پس از چاپ (تکمیلی)
            {'title': 'خدمات صحافی و برش', 'slug': 'rev-binding', 'op_type': 'print'},
            {'title': 'خدمات سلفون و یووی', 'slug': 'rev-lamination', 'op_type': 'print'},
            
            # لجستیک و سایر
            {'title': 'هزینه ارسال (دریافتی از مشتری)', 'slug': 'rev-shipping', 'op_type': 'logistics'},
            {'title': 'هزینه فوریت (Express)', 'slug': 'rev-urgent', 'op_type': 'sales'},
            {'title': 'متفرقه / ضایعات', 'slug': 'rev-waste-sale', 'op_type': 'sales'},
        ]

        # ===== COST CATEGORIES (هزینه‌ها) ===== #
        # nature='cost'
        costs = [
            # مواد اولیه مصرفی
            {'title': 'خرید کاغذ و مقوا', 'slug': 'cost-paper', 'op_type': 'material'},
            {'title': 'خرید مرکب و حلال', 'slug': 'cost-ink', 'op_type': 'material'},
            {'title': 'خرید زینک (پلیت)', 'slug': 'cost-plate', 'op_type': 'material'},
            {'title': 'خرید بنر و وینیل خام', 'slug': 'cost-media-roll', 'op_type': 'material'},
            
            # تولید و چاپ
            {'title': 'تعمیر و نگهداری ماشین‌آلات', 'slug': 'cost-maintenance', 'op_type': 'print'},
            {'title': 'هزینه چاپ ایثار (برون‌سپاری)', 'slug': 'cost-outsourcing-print', 'op_type': 'outsourcing'},
            
            # خدمات پس از چاپ
            {'title': 'چسب و ملزومات صحافی', 'slug': 'cost-glue-binding', 'op_type': 'material'},
            {'title': 'هزینه قالب‌سازی (دایکات)', 'slug': 'cost-die-cut', 'op_type': 'print'},
            
            # لجستیک
            {'title': 'هزینه پیک و باربری', 'slug': 'cost-courier', 'op_type': 'logistics'},
            {'title': 'کارتن و بسته‌بندی', 'slug': 'cost-packaging-material', 'op_type': 'logistics'},
            
            # سربار
            {'title': 'حقوق و دستمزد', 'slug': 'cost-salary', 'op_type': 'overhead'},
            {'title': 'اجاره و انرژی (برق/آب)', 'slug': 'cost-utilities', 'op_type': 'overhead'},
        ]

        # ===== INSERTION LOGIC ===== #
        self.stdout.write("Seeding Financial Categories...")
        
        for item in revenues:
            OrderFinancialCategory.objects.get_or_create(
                slug=item['slug'],
                defaults={
                    'title': item['title'],
                    'operation_type': item['op_type'],
                    'nature': 'revenue' # <--- IMPORTANT
                }
            )

        for item in costs:
            OrderFinancialCategory.objects.get_or_create(
                slug=item['slug'],
                defaults={
                    'title': item['title'],
                    'operation_type': item['op_type'],
                    'nature': 'cost' # <--- IMPORTANT
                }
            )
            
        self.stdout.write(self.style.SUCCESS("✅ Financial Categories Seeded Successfully."))