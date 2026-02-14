from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from core.models import (
    User, Role, UserRole, CustomerProfile,
    Province, City, Address,
    OrderStatusGroup, OrderStatus, Invoice
)
from apps.financial.models import Transaction
from apps.order.models import (
    OrderCostCategory, OrderCostType,
    OrderCostSheet, OrderCostReport, OrderCostItem,
)

class Command(BaseCommand):
    help = 'Create comprehensive test data for the system'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting test data creation...")
        
        try:
            with transaction.atomic():
                # 1. ایجاد گروه‌های وضعیت و وضعیت‌ها
                self._create_status_groups_and_statuses()
                
                # 2. ایجاد نقش‌ها
                self._create_roles()
                
                # 3. ایجاد کاربران
                self._create_users()
                
                # 4. ایجاد دسته‌بندی‌های هزینه
                self._create_cost_categories()
                
                # 5. ایجاد نوع هزینه‌ها
                self._create_cost_types()
                
                # 6. ایجاد سفارش نمونه
                self._create_sample_order_with_costs()
                
                self.stdout.write(self.style.SUCCESS("✅ All test data created successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))

    def _create_status_groups_and_statuses(self):
        """ایجاد گروه‌های وضعیت و وضعیت‌ها"""
        self.stdout.write("Creating status groups and statuses...")
        
        # ===== 1. GROUPS ===== #
        groups_data = [
            {"name": "ادمین", "code": "admin", "description": "مدیریت کل سیستم"},
            {"name": "مالی", "code": "financial", "description": "واحد حسابداری"},
            {"name": "طراح", "code": "designer", "description": "واحد طراحی و لیتوگرافی"},
            {"name": "چاپ", "code": "print", "description": "واحد تولید و چاپ"},
            {"name": "انبار", "code": "logistics", "description": "واحد انبار و ارسال"},
            {"name": "مشتری", "code": "customer", "description": "نمایش برای مشتری"},
        ]

        self.groups_map = {}
        for g_data in groups_data:
            group, created = OrderStatusGroup.objects.get_or_create(
                code=g_data['code'],
                defaults={
                    'name': g_data['name'],
                    'description': g_data['description'],
                    'is_system': True
                }
            )
            self.groups_map[g_data['code']] = group

        # ===== 2. STATUSES ===== #
        statuses_data = [
            # --- ADMIN ---
            {"name": "در انتظار بررسی", "internal_code": "PENDING_INITIAL_ADMIN", "status_type": "initial", "group": "admin"},
            {"name": "تایید نهایی", "internal_code": "APPROVED_APPROVE_ADMIN", "status_type": "approve", "group": "admin"},
            {"name": "رد شده توسط ادمین", "internal_code": "REJECTED_REJECT_ADMIN", "status_type": "reject", "group": "admin"},
            {"name": "لغو شده", "internal_code": "CANCELED_CANCEL_ADMIN", "status_type": "cancel", "group": "admin"},

            # --- FINANCIAL ---
            {"name": "در انتظار پرداخت", "internal_code": "PAYMENT_PENDING_PROGRESS_FINANCIAL", "status_type": "progress", "group": "financial"},
            {"name": "تایید مالی", "internal_code": "PAYMENT_APPROVED_APPROVE_FINANCIAL", "status_type": "approve", "group": "financial"},
            {"name": "رد شده توسط مالی", "internal_code": "PAYMENT_REJECTED_REJECT_FINANCIAL", "status_type": "reject", "group": "financial"},

            # --- DESIGNER ---
            {"name": "در حال طراحی", "internal_code": "DESIGN_PROGRESS_DESIGNER", "status_type": "progress", "group": "designer"},
            {"name": "تایید طراحی", "internal_code": "DESIGN_APPROVED_APPROVE_DESIGNER", "status_type": "approve", "group": "designer"},
            {"name": "رد شده توسط طراح", "internal_code": "DESIGN_REJECTED_REJECT_DESIGNER", "status_type": "reject", "group": "designer"},

            # --- PRINT (PRODUCTION) ---
            {"name": "در صف چاپ", "internal_code": "QUEUE_PROGRESS_PRINT", "status_type": "progress", "group": "print"},
            {"name": "در حال چاپ", "internal_code": "PRINTING_PROGRESS_PRINT", "status_type": "progress", "group": "print"},
            {"name": "تایید چاپ (اتمام تولید)", "internal_code": "PRINT_DONE_APPROVE_PRINT", "status_type": "approve", "group": "print"},
            {"name": "رد شده توسط چاپخانه", "internal_code": "PRINT_REJECTED_REJECT_PRINT", "status_type": "reject", "group": "print"},

            # --- LOGISTICS (WAREHOUSE) ---
            # 1. تایید ورود به انبار (Receipt) -> Approve Type
            {"name": "دریافت در انبار (آماده ارسال)", "internal_code": "READY_TO_SHIP_APPROVE_LOGISTICS", "status_type": "approve", "group": "logistics"},
            
            # 2. در حال ارسال (Dispatched) -> Progress Type
            {"name": "در حال ارسال (تحویل پیک)", "internal_code": "DISPATCHED_PROGRESS_LOGISTICS", "status_type": "progress", "group": "logistics"},
            
            # 3. رد شده
            {"name": "رد شده توسط انبار", "internal_code": "SHIPMENT_REJECTED_REJECT_LOGISTICS", "status_type": "reject", "group": "logistics"},
            
            # 4. تحویل نهایی (مشتری)
            {"name": "تحویل شده به مشتری", "internal_code": "DELIVERED_APPROVE_ADMIN", "status_type": "approve", "group": "logistics"},
        ]

        for index, s_data in enumerate(statuses_data):
            OrderStatus.objects.get_or_create(
                internal_code=s_data['internal_code'],
                defaults={
                    'name': s_data['name'],
                    'status_type': s_data['status_type'],
                    'group': self.groups_map[s_data['group']],
                    'description': f"وضعیت {s_data['name']}",
                    'is_system': True,
                    'sort_order': index + 1
                }
            )   

    def _create_roles(self):
        """ایجاد نقش‌ها"""
        self.stdout.write("Creating roles...")
        
        # نقش ادمین
        self.admin_role, _ = Role.objects.get_or_create(
            slug='admin',
            defaults={
                'name': 'مدیر سیستم',
                'description': 'دسترسی کامل به همه بخش‌ها',
                'type': 'admin',
                'is_customer': False
            }
        )
        # ادمین به همه گروه‌ها دسترسی داره
        self.admin_role.allowed_groups.set(self.groups_map.values())
        
        # نقش طراح
        self.designer_role, _ = Role.objects.get_or_create(
            slug='designer',
            defaults={
                'name': 'طراح',
                'description': 'واحد طراحی و لیتوگرافی',
                'type': 'normal',
                'is_customer': False
            }
        )
        self.designer_role.allowed_groups.set([self.groups_map['designer']])
        
        # نقش چاپخانه
        self.print_role, _ = Role.objects.get_or_create(
            slug='print',
            defaults={
                'name': 'اپراتور چاپ',
                'description': 'واحد تولید و چاپ',
                'type': 'normal',
                'is_customer': False
            }
        )
        self.print_role.allowed_groups.set([self.groups_map['print']])
        
        # نقش انباردار
        self.logistics_role, _ = Role.objects.get_or_create(
            slug='logistics',
            defaults={
                'name': 'انباردار',
                'description': 'واحد انبار و ارسال',
                'type': 'normal',
                'is_customer': False
            }
        )
        self.logistics_role.allowed_groups.set([self.groups_map['logistics']])
        
        # نقش مشتری
        self.customer_role, _ = Role.objects.get_or_create(
            slug='customer',
            defaults={
                'name': 'مشتری',
                'description': 'کاربر مشتری',
                'type': 'normal',
                'is_customer': True
            }
        )
        self.customer_role.allowed_groups.set([self.groups_map['customer']])

    def _create_users(self):
        """ایجاد کاربران تستی"""
        self.stdout.write("Creating test users...")
        
        # ایجاد استان و شهر برای آدرس
        province, _ = Province.objects.get_or_create(
            slug='tehran',
            defaults={'name': 'تهران'}
        )
        city, _ = City.objects.get_or_create(
            slug='tehran',
            defaults={'name': 'تهران', 'province': province}
        )
        
        # 1. ادمین
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@test.com',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('admin')
        admin_user.save()
        UserRole.objects.get_or_create(user=admin_user, role=self.admin_role)
        
        # 2. طراح
        self.designer_user, _ = User.objects.get_or_create(
            username='designer',
            defaults={
                'email': 'designer@test.com',
                'is_active': True,
                'is_staff': True
            }
        )
        self.designer_user.set_password('admin')
        self.designer_user.save()
        UserRole.objects.get_or_create(user=self.designer_user, role=self.designer_role)
        
        # 3. اپراتور چاپ
        self.print_user, _ = User.objects.get_or_create(
            username='print',
            defaults={
                'email': 'print@test.com',
                'is_active': True,
                'is_staff': True
            }
        )
        self.print_user.set_password('admin')
        self.print_user.save()
        UserRole.objects.get_or_create(user=self.print_user, role=self.print_role)
        
        # 4. انباردار
        self.logistics_user, _ = User.objects.get_or_create(
            username='logistics',
            defaults={
                'email': 'logistics@test.com',
                'is_active': True,
                'is_staff': True
            }
        )
        self.logistics_user.set_password('admin')
        self.logistics_user.save()
        UserRole.objects.get_or_create(user=self.logistics_user, role=self.logistics_role)
        
        # 5. مشتری
        customer_user, _ = User.objects.get_or_create(
            username='customer1',
            defaults={
                'email': 'customer@test.com',
                'is_active': True
            }
        )
        customer_user.set_password('admin')
        customer_user.save()
        UserRole.objects.get_or_create(user=customer_user, role=self.customer_role)
        
        # پروفایل مشتری
        CustomerProfile.objects.get_or_create(
            user=customer_user,
            defaults={
                'first_name': 'علی',
                'last_name': 'احمدی',
                'phone_number': '09admin789',
                'company': 'شرکت تست'
            }
        )
        
        # آدرس مشتری
        Address.objects.get_or_create(
            user=customer_user,
            defaults={
                'province': province,
                'city': city,
                'postal_code': 'admin7890',
                'address': 'خیابان ولیعصر، پلاک 123'
            }
        )
        
        self.stdout.write(self.style.SUCCESS("✅ Users created: admin, design, print, logistics, customer1"))
        self.stdout.write(self.style.WARNING("🔑 All passwords: admin"))

    def _create_cost_categories(self):
        """ایجاد دسته‌بندی‌های هزینه"""
        self.stdout.write("Creating cost categories...")
        
        categories = [
            {'title': 'کاغذ و مواد اولیه', 'slug': 'paper-material', 'cost_type': 'material'},
            {'title': 'رنگ چاپ', 'slug': 'print-ink', 'cost_type': 'print'},
            {'title': 'طراحی گرافیک', 'slug': 'graphic-design', 'cost_type': 'design'},
            {'title': 'برش و صحافی', 'slug': 'cutting-binding', 'cost_type': 'print'},
            {'title': 'بسته‌بندی', 'slug': 'packaging', 'cost_type': 'packing'},
            {'title': 'هزینه حمل', 'slug': 'shipping', 'cost_type': 'transport'},
            {'title': 'برون‌سپاری', 'slug': 'outsourcing', 'cost_type': 'storage'},
            {'title': 'سایر هزینه‌ها', 'slug': 'other-costs', 'cost_type': 'other'},
        ]
        
        for cat in categories:
            OrderCostCategory.objects.get_or_create(
                slug=cat['slug'],
                defaults={
                    'title': cat['title'],
                    'cost_type': cat['cost_type']
                }
            )

    def _create_cost_types(self):
        """ایجاد نوع هزینه‌ها"""
        self.stdout.write("Creating cost types...")
        
        cost_types = [
            'هزینه مواد اولیه',
            'هزینه نیروی کار',
            'هزینه ماشین‌آلات',
            'هزینه برق و آب',
            'هزینه حمل و نقل',
            'هزینه اداری',
        ]
        
        for ct in cost_types:
            OrderCostType.objects.get_or_create(
                title=ct,
                defaults={'slug': ct.replace(' ', '-')}
            )

    def _create_sample_order_with_costs(self):
        """ایجاد سفارش نمونه با گزارش هزینه‌ها"""
        self.stdout.write("Creating sample order with cost reports...")
        
        # فرض می‌کنیم مدل Order وجود داره (اگه نداری این قسمت رو کامنت کن)
        try:
            from core.models import Order
            
            # ایجاد سفارش نمونه
            order = Order.objects.create(
                order_code='ORD-TEST-001',
                # فیلدهای دیگه رو بر اساس مدل Order خودت اضافه کن
            )
            
            # ایجاد فاکتور
            invoice = Invoice.objects.create(
                order=order,
                invoice_number='INV-001',
                final_amount=Decimal('5000000'),
                status=Invoice.Status.PAID_FULL
            )
            
            # ایجاد تراکنش
            Transaction.objects.create(
                invoice=invoice,
                user=self.designer_user,
                amount=Decimal('5000000'),
                method='card_to_card',
                tracking_code='admin7890',
                payment_date=timezone.now(),
                status='confirmed'
            )
            
            # ایجاد سند بهای تمام شده
            cost_sheet = OrderCostSheet.objects.create(
                order=order,
                revenue_amount=Decimal('5000000')
            )
            
            # دریافت دسته‌بندی‌ها
            paper_cat = OrderCostCategory.objects.get(slug='paper-material')
            ink_cat = OrderCostCategory.objects.get(slug='print-ink')
            design_cat = OrderCostCategory.objects.get(slug='graphic-design')
            cutting_cat = OrderCostCategory.objects.get(slug='cutting-binding')
            packaging_cat = OrderCostCategory.objects.get(slug='packaging')
            shipping_cat = OrderCostCategory.objects.get(slug='shipping')
            
            cost_type_material = OrderCostType.objects.get(title='هزینه مواد اولیه')
            cost_type_labor = OrderCostType.objects.get(title='هزینه نیروی کار')
            
            # ===== 5 گزارش برای واحد چاپ ===== #
            print_reports_data = [
                {
                    'title': 'گزارش هزینه کاغذ سفارش 001',
                    'cost_type': cost_type_material,
                    'items': [
                        {'category': paper_cat, 'amount': 800000, 'desc': 'کاغذ گلاسه 150 گرم'},
                        {'category': paper_cat, 'amount': 200000, 'desc': 'کاغذ پشت'},
                    ]
                },
                {
                    'title': 'گزارش هزینه رنگ و پلیت',
                    'cost_type': cost_type_material,
                    'items': [
                        {'category': ink_cat, 'amount': 350000, 'desc': 'رنگ CMYK'},
                        {'category': ink_cat, 'amount': 150000, 'desc': 'پانتون طلایی'},
                    ]
                },
                {
                    'title': 'گزارش هزینه نیروی کار چاپ',
                    'cost_type': cost_type_labor,
                    'items': [
                        {'category': None, 'custom': 'اپراتور دستگاه چاپ', 'amount': 400000},
                        {'category': None, 'custom': 'کمک اپراتور', 'amount': 250000},
                    ]
                },
                {
                    'title': 'گزارش هزینه برش و صحافی',
                    'cost_type': cost_type_material,
                    'items': [
                        {'category': cutting_cat, 'amount': 300000, 'desc': 'برش با دستگاه گیوتین'},
                        {'category': cutting_cat, 'amount': 200000, 'desc': 'سلفون براق'},
                    ]
                },
                {
                    'title': 'گزارش هزینه کنترل کیفیت',
                    'cost_type': cost_type_labor,
                    'items': [
                        {'category': None, 'custom': 'بازرس کیفیت', 'amount': 150000},
                    ]
                },
            ]
            
            for rep_data in print_reports_data:
                report = OrderCostReport.objects.create(
                    sheet=cost_sheet,
                    submitter=self.print_user,
                    title=rep_data['title'],
                    cost_type=rep_data['cost_type'],
                    is_approved=True,
                    description='گزارش ثبت شده توسط واحد چاپ'
                )
                
                for item_data in rep_data['items']:
                    OrderCostItem.objects.create(
                        report=report,
                        catalog_item=item_data.get('category'),
                        custom_title=item_data.get('custom', ''),
                        amount=Decimal(item_data['amount']),
                        description=item_data.get('desc', '')
                    )
            
            # ===== 5 گزارش برای واحد انبار ===== #
            logistics_reports_data = [
                {
                    'title': 'گزارش هزینه بسته‌بندی اولیه',
                    'cost_type': cost_type_material,
                    'items': [
                        {'category': packaging_cat, 'amount': 120000, 'desc': 'کارتن 5 لایه'},
                        {'category': packaging_cat, 'amount': 50000, 'desc': 'نایلون استرچ'},
                    ]
                },
                {
                    'title': 'گزارش هزینه حمل داخلی',
                    'cost_type': OrderCostType.objects.get(title='هزینه حمل و نقل'),
                    'items': [
                        {'category': shipping_cat, 'amount': 200000, 'desc': 'حمل به انبار اصلی'},
                    ]
                },
                {
                    'title': 'گزارش هزینه نیروی کار انبار',
                    'cost_type': cost_type_labor,
                    'items': [
                        {'category': None, 'custom': 'انباردار', 'amount': 180000},
                        {'category': None, 'custom': 'باربر', 'amount': 120000},
                    ]
                },
                {
                    'title': 'گزارش هزینه ارسال به مشتری',
                    'cost_type': OrderCostType.objects.get(title='هزینه حمل و نقل'),
                    'items': [
                        {'category': shipping_cat, 'amount': 350000, 'desc': 'پست پیشتاز'},
                        {'category': None, 'custom': 'بیمه بسته', 'amount': 50000},
                    ]
                },
                {
                    'title': 'گزارش هزینه بسته‌بندی نهایی',
                    'cost_type': cost_type_material,
                    'items': [
                        {'category': packaging_cat, 'amount': 80000, 'desc': 'جعبه مقوایی اختصاصی'},
                        {'category': packaging_cat, 'amount': 30000, 'desc': 'چسب و لیبل'},
                    ]
                },
            ]
            
            for rep_data in logistics_reports_data:
                report = OrderCostReport.objects.create(
                    sheet=cost_sheet,
                    submitter=self.logistics_user,
                    title=rep_data['title'],
                    cost_type=rep_data['cost_type'],
                    is_approved=True,
                    description='گزارش ثبت شده توسط واحد انبار'
                )
                
                for item_data in rep_data['items']:
                    OrderCostItem.objects.create(
                        report=report,
                        catalog_item=item_data.get('category'),
                        custom_title=item_data.get('custom', ''),
                        amount=Decimal(item_data['amount']),
                        description=item_data.get('desc', '')
                    )
            
            self.stdout.write(self.style.SUCCESS(f"✅ Created order {order.order_code} with 10 cost reports"))
            
        except ImportError:
            self.stdout.write(self.style.WARNING("⚠️ Order model not found, skipping order creation"))