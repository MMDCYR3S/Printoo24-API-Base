from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import User, Order
from core.domain.commerce.order import OrderRepository
from core.domain.commerce.order import OrderCostDomainService
from core.domain.infrastructure.logger.services import AuditLogDomainService
from apps.permissions import AppPermissionChecker

class OrderCostAppService:
    """
    سرویس اپلیکیشن برای مدیریت چرخه مالی سفارشات.
    وظایف:
    1. دریافت گزارش هزینه از واحدها (Submit)
    2. مدیریت تایید/رد گزارشات توسط مالی (Approve/Reject)
    3. بستن حساب سفارش (Finalize)
    """
    def __init__(self):
        self.order_repo = OrderRepository()
        self.domain_service = OrderCostDomainService()
        self.audit_service = AuditLogDomainService()
        
    # ========== SUBMIT REPORT ========== #
    def submit_department_report(self, requester: User, order_id: int, validated_data: dict, files_list=None):
        """
        ارسال گزارش هزینه توسط پرسنل (انبار، چاپ، طراحی).
        جایگزین متد قدیمی add_cost_items.
        """
        # ===== بررسی مجوز کلی ===== #
        AppPermissionChecker.check_has_permission(requester, 'add_ordercostreport')

        # ===== دریافت سفارش ===== #
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValidationError("سفارش مورد نظر یافت نشد.")

        # ===== بررسی دسترسی فاز (Scope Validation) ===== #
        if not requester.is_superuser:
            self._validate_access_scope(requester, order)

        # ===== فراخوانی دومین سرویس ===== #
        report = self.domain_service.submit_cost_report(
            order_id=order.id,
            user=requester,
            department=validated_data['department'],
            title=validated_data['title'],
            items_data=validated_data['items'],
            attachments_data=files_list,
            description=validated_data.get('description', "")
        )
        
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=requester,
            obj=report.sheet,
            action='SUBMIT_COST_REPORT',
            changes={
                'department': validated_data['department'],
                'report_title': validated_data['title'],
                'items_count': len(validated_data['items'])
            },
            description=_(f"ثبت گزارش هزینه توسط واحد {validated_data['department']}")
        )
        
        return report

    # ========== 2. MASTER DATA (Config) ========== #
    def list_cost_types(self, user: User):
        """ لیست کردن انواع هزینه‌ها برای نمایش در دراپ‌داون """
        AppPermissionChecker.check_has_permission(user, 'view_ordercostcategory')
        return self.domain_service.get_all_categories()

    def create_cost_type(self, user: User, data: dict):
        """ تعریف نوع هزینه جدید (مثلا: چسب صحافی) """
        AppPermissionChecker.check_has_permission(user, 'add_ordercostcategory')
        category = self.domain_service.create_category(data)
        
        self.audit_service.record_log(
            user=user,
            obj=category,
            action='CREATE_COST_TYPE',
            changes={'name': category.name, 'slug': category.slug},
            description=_(f"تعریف نوع هزینه جدید: {category.name}")
        )
        return category

    def update_cost_type(self, user: User, category_id: int, data: dict):
        """ ویرایش عنوان یا کد نوع هزینه """
        AppPermissionChecker.check_has_permission(user, 'change_ordercostcategory')
        category = self.domain_service.update_category(category_id, data)
        
        self.audit_service.record_log(
            user=user,
            obj=category,
            action='UPDATE_COST_TYPE',
            changes={'updated_fields': list(data.keys())},
            description=_(f"ویرایش نوع هزینه: {category.name}")
        )
        return category

    def delete_cost_type(self, user: User, category_id: int):
        """ حذف نوع هزینه """
        AppPermissionChecker.check_has_permission(user, 'delete_ordercostcategory')
        self.domain_service.delete_category(user, category_id)
        
        self.audit_service.record_log(
            user=user,
            obj=None,
            action='DELETE_COST_TYPE',
            changes={'deleted_category_id': category_id},
            description=_("حذف نوع هزینه")
        )

    # ========== INTERNAL HELPER METHODS ========== #
    def _validate_access_scope(self, user: User, order: Order):
        """
        بررسی دقیق دسترسی کاربر به ثبت هزینه در وضعیت فعلی سفارش.
        منطق: کاربر انبار فقط زمانی می‌تواند هزینه ثبت کند که سفارش در وضعیت‌های مربوط به انبار باشد.
        """
        # ===== دریافت نقش کاربر ===== #
        if not hasattr(user, 'user_role'):
             raise PermissionDenied("کاربر فاقد نقش سیستمی است.")
             
        user_role = user.user_role
        if getattr(user_role.role, 'is_super_role', False):
             return

        # ===== بررسی وضعیت فعلی سفارش ===== #
        current_status = order.current_status
        if not current_status or not current_status.group:
            raise PermissionDenied("وضعیت فعلی سفارش نامعتبر است.")

        current_group_code = current_status.group.code
        
        # ===== بررسی دسترسی کاربر به گروه وضعیت ===== #
        allowed_codes = list(user_role.role.allowed_groups.values_list('code', flat=True))
        
        if current_group_code not in allowed_codes:
            # ===== لاگ امنیتی تلاش غیرمجاز ===== #
            self.audit_service.record_log(
                user=user,
                obj=order,
                action='SCOPE_ACCESS_DENIED',
                changes={
                    'current_stage': current_group_code,
                    'user_role': user_role.role.slug,
                    'allowed_stages': allowed_codes
                },
                description=_("تلاش غیرمجاز برای ثبت هزینه در مرحله غیرمرتبط")
            )
            raise PermissionDenied(
                f"نقش شما ({user_role.role.title}) مجاز به ثبت هزینه در مرحله '{current_status.group.name}' نیست."
            )
