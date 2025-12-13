from rest_framework.exceptions import PermissionDenied, ValidationError
from core.models import User, Order
from core.domain.commerce.order import OrderRepository
from core.domain.commerce.order import OrderCostDomainService
from apps.permissions import AppPermissionChecker

class OrderCostAppService:
    """
    سرویس اپلیکیشن برای مدیریت گزارشات هزینه.
    این سرویس توسط واحدهای مختلف (چاپ، انبار، طراحی) استفاده می‌شود.
    """
    def __init__(self):
        self.order_repo = OrderRepository()
        self.domain_service = OrderCostDomainService()

    def create_report(self, requester: User, order_id: int, validated_data: dict, files_list=None):
        """
        ایجاد گزارش هزینه جدید با بررسی دسترسی نقش کاربر به مرحله جاری سفارش.
        """
        # ===== بررسی مجوز دسترسی ===== #
        AppPermissionChecker.check_has_permission(requester, 'add_ordercostreport')

        # ===== بررسی وجود سفارش ===== #
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValidationError("سفارش یافت نشد.")

        # ===== بررسی دسترسی کاربر ===== #
        if not requester.is_superuser:
            self._validate_access_scope(requester, order)

        # ===== ایجاد گزارش ===== #
        report = self.domain_service.create_cost_report(
            order=order,
            user=requester,
            title=validated_data['title'],
            description=validated_data.get('description'),
            items_data=validated_data['items'],
            attachments_data=files_list
        )
        
        return report

    def _validate_access_scope(self, user: User, order: Order):
        """
        بررسی می‌کند که آیا کاربر اجازه دارد در 'وضعیت فعلی سفارش' هزینه ثبت کند؟
        مثال:
        - اگر سفارش در مرحله 'Design' است، کاربر 'چاپ' نباید بتواند هزینه ثبت کند.
        - اگر کاربر 'Financial' است، معمولاً روی همه مراحل دسترسی دارد (بسته به تنظیمات Role).
        """
        # ===== دریافت نقش کاربر ===== #
        user_role_rel = user.user_role.select_related('role').first()
        if not user_role_rel:
            raise PermissionDenied("شما هیچ نقش فعالی در سیستم ندارید.")
        
        role = user_role_rel.role
        
        if getattr(role, 'is_super_role', False):
            return

        # ===== دریافت کد گروه وضعیت ===== #
        current_status = order.current_status
        if not current_status or not current_status.group:
            raise PermissionDenied("وضعیت سفارش نامعتبر است.")

        current_group_code = current_status.group.code
        if current_group_code not in role.allowed_status_groups:
            raise PermissionDenied(
                f"شما اجازه ثبت هزینه برای سفارشی که در واحد '{current_status.group.name}' است را ندارید."
            )

    # ========== بخش نوع هزینه ها ========== #
    def list_cost_types(self, user: User):
        """ لیست همه انواع هزینه """
        AppPermissionChecker.check_has_permission(user, 'view_ordercosttype')
        return self.domain_service.type_repo.get_all() 

    def create_cost_type(self, user: User, data: dict):
        """ تعریف نوع هزینه جدید """
        AppPermissionChecker.check_has_permission(user, 'add_ordercosttype')
        return self.domain_service.create_cost_type(user, data)

    def update_cost_type(self, user: User, type_id: int, data: dict):
        """ ویرایش نوع هزینه """
        AppPermissionChecker.check_has_permission(user, 'change_ordercosttype')
        return self.domain_service.update_cost_type(type_id, user, data)

    def delete_cost_type(self, user: User, type_id: int):
        """ حذف نوع هزینه """
        AppPermissionChecker.check_has_permission(user, 'delete_ordercosttype')
        self.domain_service.delete_cost_type(type_id, user)
