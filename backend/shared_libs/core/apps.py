from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _

class CoreConfig(AppConfig):
    """
    یک اپلیکیشن مشترک بین دو پروژه ما
    کارایی این اپلیکیشن به صورتی است  که مدل های مشترک، لایه های منطقی مشترک و همچنین
    گردش کارهایی که مابین پروژه سمت مشتری و ادمین مشترک هست رو مدیریت میکنه.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        import core.signals
        # post_migrate.connect(create_initial_statuses, sender=self)
        
        
# def create_initial_statuses(sender, **kwargs):
#     """
#     این تابع پس از هر بار migrate اجرا می‌شود و چک می‌کند
#     اگر وضعیت‌های حیاتی وجود ندارند، آن‌ها را می‌سازد.
#     """
    
#     from core.models import OrderStatusGroup, OrderStatus
    
#     admin_group, created = OrderStatusGroup.objects.get_or_create(
#         code='admin',
#         defaults={
#             'name': 'مدیر سیستم',
#             'description': 'گروه پیش‌فرض برای وضعیت‌های سیستمی',
#             'is_system': True
#         }
#     )
    
#     required_statuses = [
#         ('pending', 'در انتظار بررسی', 'progress', 1),
#         ('shipped', 'ارسال شد', 'approve', 90),
#         ('delivered', 'تحویل شده', 'approve', 99),
#         ('cancelled', 'لغو شده', 'cancel', 100),
#     ]

#     for internal_code, name, s_type, sort in required_statuses:
#         if not OrderStatus.objects.filter(internal_code=internal_code).exists():
#             OrderStatus.objects.create(
#                 group=admin_group,
#                 name=name,
#                 internal_code=internal_code,
#                 status_type=s_type,
#                 sort_order=sort,
#                 is_system=True,
#                 description='ایجاد شده توسط سیستم به صورت خودکار'
#             )
#             print(f"✅ System Status Created: {internal_code}")
