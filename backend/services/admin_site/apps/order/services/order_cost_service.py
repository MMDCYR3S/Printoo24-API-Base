from typing import Dict, List, Any
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied, ValidationError

from core.models import (
    User, Order
)
from apps.order.models import *
from apps.order.domain_services import OrderCostService
from apps.support.services import LoggerService
from apps.permissions import AppPermissionChecker

class OrderCostAppService:
    """
    سرویس اپلیکیشن برای مدیریت چرخه مالی سفارشات (توسط واحدها).
    وظایف:
    1. دریافت گزارش هزینه از واحدها (Submit)
    2. مدیریت Master Data (Cost Types)
    3. بررسی دسترسی مرحله‌ای (Stage Scope)
    """

    def __init__(self):
        self.domain_service = OrderCostService()
        self.audit_service = LoggerService()
        
    # ========== SUBMIT REPORT ========== #
    def submit_department_report(self, requester: User, order_id: int, validated_data: dict, files_list=None):
        """
        ارسال گزارش هزینه توسط پرسنل (انبار، چاپ، طراحی).
        این متد گزارش و آیتم‌هایش را می‌سازد.
        """
        # ===== بررسی مجوز کلی ===== #
        AppPermissionChecker.check_has_permission(requester, 'add_ordercostreport')

        # ===== دریافت سفارش ===== #
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise ValidationError("سفارش مورد نظر یافت نشد.")
        
        # ===== بررسی دسترسی فاز (Scope Validation) ===== #
        if not requester.is_superuser:
            self._validate_access_scope(requester, order)
        # ===== اطمینان از وجود سند مالی ===== #
        sheet = self._ensure_sheet_exists(order_id)
        
        # ===== فراخوانی دومین سرویس ===== #
        report = OrderCostReport.objects.create(
            sheet=sheet,
            submitter=requester,
            department=validated_data['department'],
            title=validated_data['title'],
            description=validated_data.get('description', ""),
            is_approved=False
        )
        # ===== ایجاد آیتم های مربوط به هزینه ===== #
        items_data = validated_data.get('items', [])
        new_items = []
        for item_data in items_data:
            category = None
            if item_data.get('category_id'):
                category = OrderCostCategory.objects.get_by_id(item_data['category_id'])
                
            new_items.append(OrderCostItem(
                report=report,
                catalog_item=category,
                custom_title=item_data.get('custom_title'),
                amount=item_data.get('amount', 0),
                description=item_data.get('description', '')
            ))
        # ===== اگر آیتم جدید بود ===== #
        if new_items:
            OrderCostItem.objects.bulk_create_items(new_items)
        # ===== محاسبه قیمت مجدد ===== #
        self.domain_service.recalculate_sheet_totals(sheet)
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=requester,
            obj=report.sheet,
            action='SUBMIT_COST_REPORT',
            changes={
                'department': validated_data['department'],
                'report_title': validated_data['title'],
                'items_count': len(new_items)
            },
            description=_(f"ثبت گزارش هزینه توسط واحد {validated_data['department']}")
        )
        
        return report

    # ========== 2. MASTER DATA (Config) ========== #
    def list_cost_types(self, user: User):
        """ لیست کردن انواع هزینه‌ها """
        AppPermissionChecker.check_has_permission(user, 'view_ordercostcategory')
        return OrderCostCategory.objects.get_all_active()

    def create_cost_type(self, user: User, data: dict):
        """ تعریف نوع هزینه جدید (مثلا: چسب صحافی) """
        AppPermissionChecker.check_has_permission(user, 'add_ordercostcategory')
        if OrderCostCategory.objects.get_by_slug(data.get('slug')):
             raise ValidationError("کد دسته‌بندی تکراری است.")

        category = OrderCostCategory.objects.create(**data)
        # ===== ثبت لاگ ===== #
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
        # ===== دریافت ===== #
        try:
            category = OrderCostCategory.objects.get(id=category_id)
        except OrderCostCategory.DoesNotExist:
            raise ValidationError("دسته‌بندی یافت نشد.")
        # ===== بروزرسانی ===== #
        for key, value in data.items():
            setattr(category, key, value)
        category.save()
        
        self.audit_service.record_log(
            user=user,
            obj=category,
            action='UPDATE_COST_TYPE',
            changes={'updated_fields': list(data.keys())},
            description=_(f"ویرایش نوع هزینه: {category.title}")
        )
        return category

    def delete_cost_type(self, user: User, category_id: int):
        """ حذف نوع هزینه """
        AppPermissionChecker.check_has_permission(user, 'delete_ordercostcategory')
        try:
            category = OrderCostCategory.objects.get(id=category_id)
        except OrderCostCategory.DoesNotExist:
            raise ValidationError("دسته‌بندی یافت نشد.")
        
        cat_name = category.title
        category.delete()
        
        self.audit_service.record_log(
            user=user,
            obj=None,
            action='DELETE_COST_TYPE',
            changes={'deleted_category_id': category_id},
            description=_(f"حذف نوع هزینه: {cat_name}")
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
                f"نقش شما ({user_role.role.name}) مجاز به ثبت هزینه در مرحله '{current_status.group.name}' نیست."
            )
        
    def _ensure_sheet_exists(self, order_id: int) -> OrderCostSheet:
        """ اگر شیت وجود نداشت، یکی بساز """
        sheet = OrderCostSheet.objects.get_by_order_id(order_id)
        if not sheet:
            sheet = OrderCostSheet.objects.create(order_id=order_id)
        return sheet
