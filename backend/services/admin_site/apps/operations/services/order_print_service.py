from rest_framework.exceptions import ValidationError

from core.models import User
from core.domain.commerce.order import OrderRepository, OrderPrintDomainService
from apps.permissions import AppPermissionChecker

# ========== Order Print App Service ========== #
class OrderPrintAppService:
    """
    سرویس اپلیکیشن مخصوص واحد چاپ.
    مسئولیت: هماهنگی بین کاربر، سفارش و سرویس دامنه چاپ.
    """
    def __init__(self):
        self.order_repo = OrderRepository()
        self.domain_service = OrderPrintDomainService()

    def create_print_usage(self, user: User, order_id: int, validated_data: dict, files_list=None):
        """
        ثبت مصرف متریال توسط اپراتور چاپ.
        """
        # ===== چک کردن دسترسی ===== #
        AppPermissionChecker.check_has_permission(user, 'add_orderprintreport')

        # ===== دریافت اطلاعات مرتبط ===== #
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValidationError("سفارش مورد نظر یافت نشد.")

        # ===== ایجاد گزارش ===== #
        report = self.domain_service.register_usage_report(
            order=order,
            user=user,
            title=validated_data['title'],
            description=validated_data.get('description', ''),
            items_data=validated_data['items'],
            attachments_list=files_list
        )
        
        return report
    
    def get_order_print_reports(self, user: User, order_id: int):
        """ لیست گزارشات مصرف یک سفارش """
        AppPermissionChecker.check_has_permission(user, 'view_orderprintreport')
        return self.domain_service.report_repo.get_reports_by_order(order_id)

    def update_print_usage(self, user: User, report_id: int, validated_data: dict, files_list=None):
        """ ویرایش گزارش مصرف """
        AppPermissionChecker.check_has_permission(user, 'change_orderprintreport')
        
        return self.domain_service.update_print_report(
            report_id=report_id,
            user=user,
            data=validated_data,
            new_attachments=files_list
        )

    def delete_print_usage(self, user: User, report_id: int):
        """ حذف گزارش مصرف """
        AppPermissionChecker.check_has_permission(user, 'delete_orderprintreport')
        self.domain_service.delete_report(report_id, user)
