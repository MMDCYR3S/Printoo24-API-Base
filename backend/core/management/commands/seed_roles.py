from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from core.models import Role

class Command(BaseCommand):
    help = 'Creates default system roles and assigns basic permissions'

    def handle(self, *args, **options):
        roles_data = [
            {
                'code': 'admin', 
                'name': 'ادمین', 
                'desc': 'دسترسی کامل به مدیریت سفارشات و کاربران داخلی',
            },
            {
                'code': 'finance', 
                'name': 'واحد مالی', 
                'desc': 'صدور فاکتور و تایید پرداخت',
                'perms': ['view_invoice', 'change_invoice', 'view_transaction']
            },
            {
                'code': 'designer', 
                'name': 'طراح', 
                'desc': 'بررسی و آپلود فایل‌های طراحی',
                'perms': ['view_orderitemfile', 'change_orderitemfile']
            },
            {
                'code': 'qc', 
                'name': 'کنترل کیفیت', 
                'desc': 'تایید یا رد کیفیت نهایی',
                'perms': ['view_order', 'change_order_status_qc']
            },
            {
                'code': 'print', 
                'name': 'واحد چاپ', 
                'desc': 'مشاهده صف چاپ و اعلام مصرف مواد',
                'perms': ['view_orderitem']
            },
            {
                'code': 'warehouse', 
                'name': 'انباردار', 
                'desc': 'بسته‌بندی و ارسال',
                'perms': ['view_shipment', 'change_shipment']
            },
            {
                'code': 'marketing', 
                'name': 'مارکتینگ', 
                'desc': 'مدیریت مشتریان و تخفیف‌ها',
                'perms': ['view_customerprofile', 'view_discount']
            },
            {
                'code': 'customer', 
                'name': 'مشتری', 
                'desc': 'کاربر عادی سایت',
                'is_customer': True,
                'perms': []
            },
        ]

        for role_info in roles_data:
            role, created = Role.objects.get_or_create(
                code=role_info['code'],
                defaults={
                    'name': role_info['name'],
                    'description': role_info['desc'],
                    'is_customer': role_info.get('is_customer', False)
                }
            )
            if role_info['perms']:
                perms = Permission.objects.filter(codename__in=role_info['perms'])
                role.permissions.set(perms)

            self.stdout.write(self.style.SUCCESS(f"Role '{role.name}' synced."))