from rest_framework.exceptions import PermissionDenied, ValidationError
from core.models import User, Order
from core.domain.commerce.order import OrderRepository
from core.domain.commerce.order import OrderCostDomainService
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
        
        return report

    # ========== 2. MASTER DATA (Config) ========== #
    def list_cost_types(self, user: User):
        """ لیست کردن انواع هزینه‌ها برای نمایش در دراپ‌داون """
        AppPermissionChecker.check_has_permission(user, 'view_ordercostcategory')
        return self.domain_service.get_all_categories()

    def create_cost_type(self, user: User, data: dict):
        """ تعریف نوع هزینه جدید (مثلا: چسب صحافی) """
        AppPermissionChecker.check_has_permission(user, 'add_ordercostcategory')
        return self.domain_service.create_category(data)

    def update_cost_type(self, user: User, category_id: int, data: dict):
        """ ویرایش عنوان یا کد نوع هزینه """
        AppPermissionChecker.check_has_permission(user, 'change_ordercostcategory')
        return self.domain_service.update_category(category_id, data)

    def delete_cost_type(self, user: User, category_id: int):
        """ حذف نوع هزینه """
        AppPermissionChecker.check_has_permission(user, 'delete_ordercostcategory')
        self.domain_service.delete_category(user, category_id)

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
            raise PermissionDenied(
                f"نقش شما ({user_role.role.title}) مجاز به ثبت هزینه در مرحله '{current_status.group.name}' نیست."
            )
