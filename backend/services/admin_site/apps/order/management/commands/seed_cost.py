from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.utils import timezone
from decimal import Decimal

# هێنانەناوەوەی مۆدێلەکان (ڕێڕەوەکان بەپێی پرۆژەکەت بپشکنە)
from core.models import (
    User, Role, UserRole, CustomerProfile,
    Province, City, Address,
    OrderStatusGroup, OrderStatus, Invoice
)
# ئەگەر مۆدێلەکان لە ئەپەکانی دیکەدان، ئەم هێنانەناوەوانەی خوارەوە چالاک بکە:
# from apps.financial.models import Transaction, Invoice
# from apps.order.models import Order, OrderCostCategory ...

class Command(BaseCommand):
    help = 'نوێکردنەوەی تەواوی سیستەم: سڕینەوەی بارودۆخەکان و دروستکردنی داتای ١٠ قۆناغی نوێ'

    def handle(self, *args, **kwargs):
        self.stdout.write("⚠️ لە ئامادەکاریدایە بۆ نوێکردنەوەی داتاکان...")

        try:
            with transaction.atomic():
                # ١. سڕینەوەی داتا کۆنەکان (داواکارییەکان و بارودۆخەکان)
                self._clean_existing_data()

                # ٢. دروستکردن/نوێکردنەوەی ژێرخان (پارێزگا و شار) - چارەسەرکردنی هەڵەی Integrity
                self._create_infrastructure()

                # ٣. دروستکردنی گرووپەکان و ١٠ بارودۆخی نوێ
                self._create_status_groups_and_statuses()
                
                # ٤. دروستکردنی ڕۆڵەکان
                self._create_roles()
                
                # ٥. دروستکردنی بەکارهێنەران
                self._create_users()
                
                # ٦. (ئارەزوومەندانە) دروستکردنی داواکاری تاقیکاری بۆ بینینی ڕەوتی کار
                # self._create_sample_order()

                self.stdout.write(self.style.SUCCESS("✅ پرۆسەکە بە سەرکەوتووی ئەنجام درا. بارودۆخە نوێیەکان جێگیر کران."))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ هەڵە: {e}"))
            import traceback
            traceback.print_exc()

    def _clean_existing_data(self):
        """
        سڕینەوەی داتا کۆنەکان بۆ ڕێگریکردن لە تێکەڵبوون.
        ڕیزبەندی سڕینەوە گرنگە (بەهۆی Foreign Key).
        """
        self.stdout.write("🧹 لە سڕینەوەی داتا کۆنەکاندایە...")
        
        # سەرەتا دەبێت داواکارییەکان و لۆگەکان بسڕێنەوە چونکە بەسترابوونەوە بە بارودۆخەکانەوە
        # وا گریمانە دەکرێت کە مۆدێلی Order لە core دایە یان هێنراوەتە ناوەوە
        from core.models import Order, OrderItem, OrderStateLog
        
        # ئەگەر مۆدێلی داراییت هەیە، سەرەتا ئەوان بسڕەوە
        # Transaction.objects.all().delete()
        # Invoice.objects.all().delete()
        
        OrderStateLog.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        
        # ئێستا بارودۆخەکان دەسڕینەوە
        count_status = OrderStatus.objects.all().delete()[0]
        count_groups = OrderStatusGroup.objects.all().delete()[0]
        
        self.stdout.write(f"   - {count_status} بارودۆخ سڕایەوە.")
        self.stdout.write(f"   - {count_groups} گرووپی بارودۆخ سڕایەوە.")

    def _create_infrastructure(self):
        """
        دروستکردنی پارێزگا و شار بە مێتۆدی update_or_create بۆ ڕێگریکردن لە هەڵەی Duplicate Key
        """
        self.stdout.write("🏗 دروستکردنی ژێرخان (پارێزگا/شار)...")
        
        # بەکارهێنانی update_or_create لەجیاتی create ی بەتاڵ
        # ئەم هەڵەیەت بۆ چارەسەر دەکات چونکە ئەگەر slug بوونی هەبێت، تەنها نوێی دەکاتەوە.
        self.province, _ = Province.objects.update_or_create(
            slug='sulaymaniyah', # گۆڕدرا بۆ سلێمانی بەپێی سیستەمەکە
            defaults={'name': 'سلێمانی'}
        )
        
        self.city, _ = City.objects.update_or_create(
            slug='sulaymaniyah',
            defaults={'name': 'سلێمانی', 'province': self.province}
        )

    def _create_status_groups_and_statuses(self):
        self.stdout.write("🔄 لە دروستکردنی ١٠ بارودۆخی نوێدایە...")
        
        # ===== ١. گرووپەکان =====
        groups_def = [
            {"code": "admin", "name": "ئەدمینی سیستەم"},
            {"code": "designer", "name": "یەکەی دیزاین"},
            {"code": "print", "name": "یەکەی چاپ"},
            {"code": "logistics", "name": "یەکەی کۆگا"},
            {"code": "financial", "name": "یەکەی دارایی"},
            {"code": "customer", "name": "کڕیار"},
        ]

        self.groups_map = {}
        for g in groups_def:
            group, _ = OrderStatusGroup.objects.get_or_create(
                code=g['code'],
                defaults={
                    'name': g['name'],
                    'is_system': True,
                    'description': f"گرووپی کاری {g['name']}"
                }
            )
            self.groups_map[g['code']] = group

        # ===== ٢. بارودۆخەکان (١٠ قۆناغی ورد) =====
        statuses_def = [
            # 1
            {"sort": 1, "name": "چاوەڕێی پشکنین", "code": "PENDING_INITIAL_ADMIN", "type": "initial", "group": "admin"},
            # 2
            {"sort": 2, "name": "لە قۆناغی دیزایندایە", "code": "DESIGNING_PROGRESS_DESIGNER", "type": "progress", "group": "designer"},
            # 3
            {"sort": 3, "name": "ڕەتکرایەوە لەلایەن دیزاینەرەوە", "code": "DESIGN_REJECTED_REJECT_DESIGNER", "type": "reject", "group": "designer"},
            # 4
            {"sort": 4, "name": "لە چاپکردندایە", "code": "PRINTING_PROGRESS_PRINT", "type": "progress", "group": "print"},
            # 5
            {"sort": 5, "name": "ڕەتکرایەوە لەلایەن چاپەوە", "code": "PRINT_REJECTED_REJECT_PRINT", "type": "reject", "group": "print"},
            # 6
            {"sort": 6, "name": "نێردرا بۆ کۆگا", "code": "SENT_TO_WAREHOUSE_PROGRESS_LOGISTICS", "type": "progress", "group": "logistics"},
            # 7
            {"sort": 7, "name": "وەرگیرا لەلایەن کۆگاوە", "code": "RECEIVED_IN_WAREHOUSE_APPROVE_LOGISTICS", "type": "approve", "group": "logistics"},
            # 8
            {"sort": 8, "name": "ڕەتکرایەوە لەلایەن کۆگاوە", "code": "WAREHOUSE_REJECTED_REJECT_LOGISTICS", "type": "reject", "group": "logistics"},
            # 9
            {"sort": 9, "name": "گەیەندراوە", "code": "DELIVERED_APPROVE_LOGISTICS", "type": "approve", "group": "logistics"},
            # 10
            {"sort": 10, "name": "هەڵوەشاوەتەوە", "code": "CANCELLED_CANCEL_ADMIN", "type": "cancel", "group": "admin"},
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
                    'description': f"بارودۆخی ژمارە {s['sort']}"
                }
            )

    def _create_roles(self):
        self.stdout.write("👤 دروستکردنی ڕۆڵەکان...")
        
        # پێناسەکردنی ڕۆڵەکان بە دەسەڵاتی تایبەتەوە
        roles_data = [
            ('admin', 'بەڕێوەبەری گشتی', 'admin', False, self.groups_map.values()),
            ('designer', 'دیزاینەر', 'normal', False, [self.groups_map['designer']]),
            ('print', 'ئۆپەراتۆری چاپ', 'normal', False, [self.groups_map['print']]),
            ('logistics', 'کۆگادار', 'normal', False, [self.groups_map['logistics']]),
            ('financial', 'ژمێریار', 'normal', False, [self.groups_map['financial']]),
            ('customer', 'کڕیار', 'normal', True, [self.groups_map['customer']]),
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
        self.stdout.write("👥 دروستکردنی بەکارهێنەرانی تاقیکاری...")
        
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
            
            # بەستنەوەی ڕۆڵ
            UserRole.objects.get_or_create(user=user, role=self.roles_map[role_slug])
            
            # ئەگەر کڕیارە، پرۆفایل دروست بکەین
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
                        'address': 'تاقیکاری',
                        'postal_code': '11111111'
                    }
                )