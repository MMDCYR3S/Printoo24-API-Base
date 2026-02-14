from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.utils import timezone
from decimal import Decimal

# ایمپورت مدل‌ها (مسیرها را طبق پروژه خودتان چک کنید)
from core.models import (
    User, Role, UserRole, CustomerProfile,
    Province, City, Address,
    OrderStatusGroup, OrderStatus, Invoice
)
# اگر مدل‌ها در اپ‌های دیگر هستند، ایمپورت‌های زیر را فعال کنید:
# from apps.financial.models import Transaction, Invoice
# from apps.order.models import Order, OrderCostCategory ...

class Command(BaseCommand):
    help = 'بازنشانی کامل سیستم: پاکسازی وضعیت‌ها و ایجاد داده‌های ۱۰ مرحله‌ای جدید'

    def handle(self, *args, **kwargs):
        self.stdout.write("⚠️ در حال آماده‌سازی برای بازنشانی داده‌ها...")

        try:
            with transaction.atomic():
                # 1. پاکسازی داده‌های قدیمی (سفارشات و وضعیت‌ها)
                self._clean_existing_data()

                # 2. ایجاد/بروزرسانی زیرساخت (استان و شهر) - رفع خطای Integrity
                self._create_infrastructure()

                # 3. ایجاد گروه‌ها و ۱۰ وضعیت جدید
                self._create_status_groups_and_statuses()
                
                # 4. ایجاد نقش‌ها
                self._create_roles()
                
                # 5. ایجاد کاربران
                self._create_users()
                
                # 6. (اختیاری) ایجاد سفارش تست برای دیدن جریان کار
                # self._create_sample_order()

                self.stdout.write(self.style.SUCCESS("✅ عملیات با موفقیت انجام شد. وضعیت‌های جدید جایگزین شدند."))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ خطا: {e}"))
            import traceback
            traceback.print_exc()

    def _clean_existing_data(self):
        """
        پاک کردن داده‌های قدیمی برای جلوگیری از تداخل.
        ترتیب پاک کردن مهم است (بخاطر Foreign Key).
        """
        self.stdout.write("🧹 در حال پاکسازی داده‌های قدیمی...")
        
        # ابتدا سفارشات و لاگ‌ها باید پاک شوند چون به وضعیت‌ها متصل هستند
        # فرض بر این است که مدل Order در core است یا ایمپورت شده
        from core.models import Order, OrderItem, OrderStateLog
        
        # اگر مدل‌های مالی دارید، اول آن‌ها را پاک کنید
        # Transaction.objects.all().delete()
        # Invoice.objects.all().delete()
        
        OrderStateLog.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        
        # حالا وضعیت‌ها را پاک می‌کنیم
        count_status = OrderStatus.objects.all().delete()[0]
        count_groups = OrderStatusGroup.objects.all().delete()[0]
        
        self.stdout.write(f"   - {count_status} وضعیت حذف شد.")
        self.stdout.write(f"   - {count_groups} گروه وضعیت حذف شد.")

    def _create_infrastructure(self):
        """
        ایجاد استان و شهر با متد update_or_create برای جلوگیری از خطای Duplicate Key
        """
        self.stdout.write("🏗 ایجاد زیرساخت (استان/شهر)...")
        
        # استفاده از update_or_create بجای create خالی
        # این خطای شما را برطرف می‌کند چون اگر slug وجود داشته باشد، فقط آپدیت می‌کند.
        self.province, _ = Province.objects.update_or_create(
            slug='esfahan', # یا 'thrn' اگر در دیتابیس شما اینطور است
            defaults={'name': 'اصفهان'}
        )
        
        self.city, _ = City.objects.update_or_create(
            slug='esfahan',
            defaults={'name': 'اصفهان', 'province': self.province}
        )

    def _create_status_groups_and_statuses(self):
        self.stdout.write("🔄 در حال ایجاد ۱۰ وضعیت جدید...")
        
        # ===== 1. گروه‌ها =====
        groups_def = [
            {"code": "admin", "name": "ادمین سیستم"},
            {"code": "designer", "name": "واحد طراحی"},
            {"code": "print", "name": "واحد چاپ"},
            {"code": "logistics", "name": "واحد انبار"},
            {"code": "financial", "name": "واحد مالی"},
            {"code": "customer", "name": "مشتری"},
        ]

        self.groups_map = {}
        for g in groups_def:
            group, _ = OrderStatusGroup.objects.get_or_create(
                code=g['code'],
                defaults={
                    'name': g['name'],
                    'is_system': True,
                    'description': f"گروه کاری {g['name']}"
                }
            )
            self.groups_map[g['code']] = group

        # ===== 2. وضعیت‌ها (۱۰ مرحله دقیق) =====
        statuses_def = [
            # 1
            {"sort": 1, "name": "در انتظار بررسی", "code": "PENDING_INITIAL_ADMIN", "type": "initial", "group": "admin"},
            # 2
            {"sort": 2, "name": "در حال طراحی", "code": "DESIGNING_PROGRESS_DESIGNER", "type": "progress", "group": "designer"},
            # 3
            {"sort": 3, "name": "رد شده توسط طراح", "code": "DESIGN_REJECTED_REJECT_DESIGNER", "type": "reject", "group": "designer"},
            # 4
            {"sort": 4, "name": "در حال چاپ", "code": "PRINTING_PROGRESS_PRINT", "type": "progress", "group": "print"},
            # 5
            {"sort": 5, "name": "رد شده توسط چاپ", "code": "PRINT_REJECTED_REJECT_PRINT", "type": "reject", "group": "print"},
            # 6
            {"sort": 6, "name": "ارسال شده به انبار", "code": "SENT_TO_WAREHOUSE_PROGRESS_LOGISTICS", "type": "progress", "group": "logistics"},
            # 7
            {"sort": 7, "name": "دریافت توسط انبار", "code": "RECEIVED_IN_WAREHOUSE_APPROVE_LOGISTICS", "type": "approve", "group": "logistics"},
            # 8
            {"sort": 8, "name": "رد شده توسط انبار", "code": "WAREHOUSE_REJECTED_REJECT_LOGISTICS", "type": "reject", "group": "logistics"},
            # 9
            {"sort": 9, "name": "تحویل‌شده", "code": "DELIVERED_APPROVE_LOGISTICS", "type": "approve", "group": "logistics"},
            # 10
            {"sort": 10, "name": "لغو شده", "code": "CANCELLED_CANCEL_ADMIN", "type": "cancel", "group": "admin"},
        ]

        for s in statuses_def:
            OrderStatus.objects.update_or_create(
                internal_code=s['code'],
                defaults={
                    'name': s['name'],
                    'sort_order': s['sort'],
                    'status_type': s['type'],
                    'group': self.groups_map[s['group']],
                    'is_system': True,
                    'description': f"وضعیت شماره {s['sort']}"
                }
            )

    def _create_roles(self):
        self.stdout.write("👤 ایجاد نقش‌ها...")
        
        # تعریف نقش‌ها با دسترسی‌های خاص
        roles_data = [
            ('admin', 'مدیر کل', 'admin', False, self.groups_map.values()),
            ('designer', 'طراح', 'normal', False, [self.groups_map['designer']]),
            ('print', 'اپراتور چاپ', 'normal', False, [self.groups_map['print']]),
            ('logistics', 'انباردار', 'normal', False, [self.groups_map['logistics']]),
            ('financial', 'حسابدار', 'normal', False, [self.groups_map['financial']]),
            ('customer', 'مشتری', 'normal', True, [self.groups_map['customer']]),
        ]

        self.roles_map = {}
        for slug, name, r_type, is_cust, groups in roles_data:
            role, _ = Role.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'type': r_type,
                    'is_customer': is_cust
                }
            )
            role.allowed_groups.set(groups)
            self.roles_map[slug] = role

    def _create_users(self):
        self.stdout.write("👥 ایجاد کاربران تستی...")
        
        users = [
            ('admin', 'admin@printoo.ir', 'admin'),
            ('designer', 'design@printoo.ir', 'designer'),
            ('printer', 'print@printoo.ir', 'print'),
            ('warehouse', 'store@printoo.ir', 'logistics'),
            ('finance', 'money@printoo.ir', 'financial'),
            ('customer1', 'cust@gmail.com', 'customer'),
        ]

        for username, email, role_slug in users:
            user, created = User.objects.update_or_create(
                username=username,
                defaults={
                    'email': email,
                    'is_active': True,
                    'is_staff': (role_slug != 'customer'),
                    'is_superuser': (role_slug == 'admin')
                }
            )
            if created:
                user.set_password('123456')
                user.save()
            
            # اتصال نقش
            UserRole.objects.get_or_create(user=user, role=self.roles_map[role_slug])
            
            # اگر مشتری است، پروفایل بسازیم
            if role_slug == 'customer':
                CustomerProfile.objects.update_or_create(
                    user=user,
                    defaults={'phone_number': '09121234567'}
                )
                Address.objects.get_or_create(
                    user=user,
                    defaults={
                        'province': self.province,
                        'city': self.city,
                        'address': 'تست',
                        'postal_code': '11111111'
                    }
                )