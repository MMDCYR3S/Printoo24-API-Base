from typing import Dict, List, Any

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.core.files.uploadedfile import UploadedFile
from rest_framework.exceptions import PermissionDenied, ValidationError

from core.models import (
    User, Order
)
from apps.order.models import *
from apps.order.domain_services import OrderFinancialService, OrderFinancialType
from apps.support.services import LoggerService
from apps.permissions import AppPermissionChecker


class OrderFinancialAppService:
    """
    سرویس اپلیکیشن برای مدیریت چرخه مالی سفارشات (توسط واحدها).
    وظایف:
    1. دریافت گزارش هزینه از واحدها (Submit)
    2. مدیریت Master Data (Financial Types)
    3. بررسی دسترسی مرحله‌ای (Stage Scope)
    """

    def __init__(self):
        self.domain_service = OrderFinancialService()
        self.audit_service = LoggerService()
        
    # ===== SUBMIT REPORT (FORCED COST NATURE) ===== #
    @transaction.atomic
    def submit_department_report(self, requester: User, order_id: int, validated_data: dict, financial_tag_id: int = None, attachments: List[UploadedFile] = None) -> OrderFinancialReport:
        """
        ثبت گزارش هزینه توسط واحدهای عملیاتی.
        نکته: در این متد، ماهیت گزارش (nature) همیشه 'cost' ست می‌شود.
        """
        # ===== بررسی مجوز سطح دسترسی ===== #
        AppPermissionChecker.check_has_permission(requester, 'add_orderfinancialreport')

        # ===== دریافت سفارش ===== #
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise ValidationError("سفارش یافت نشد.")

        # ===== بررسی Scope دسترسی مرحله‌ای ===== #
        if not requester.is_superuser:
            self._validate_access_scope(requester, order)

        # ===== اطمینان از وجود سند مالی ===== #
        sheet = self._ensure_sheet_exists(order_id)
        
        # ===== دریافت تگ مالی ===== #
        financial_tag = None
        if financial_tag_id:
            financial_tag = OrderFinancialType.objects.filter(id=financial_tag_id).first()

        # ===== ایجاد هدر گزارش (اجبار بر هزینه بودن) ===== #
        report = OrderFinancialReport.objects.create(
            sheet=sheet,
            submitter=requester,
            financial_tag=financial_tag,
            title=validated_data['title'],
            nature='cost',  # ===== فقط هزینه مجاز است ===== #
            description=validated_data.get('description', ""),
            is_approved=False
        )

        # ===== پردازش اقلام ===== #
        items_data = validated_data.get('items', [])
        new_items = []
        for item_data in items_data:
            category = None
            if item_data.get('catalog_id'):
                category = OrderFinancialCategory.objects.filter(pk=item_data['catalog_id']).first()
            
            new_items.append(OrderFinancialItem(
                report=report,
                category=category,
                custom_title=item_data.get('custom_title'),
                amount=item_data.get('amount', 0),
                description=item_data.get('description', '')
            ))
        
        if new_items:
            OrderFinancialItem.objects.bulk_create(new_items)

        # ===== ذخیره فایل‌های پیوست ===== #
        if attachments:
            self._create_attachments(report, attachments)

        # ===== بروزرسانی محاسبات شیت ===== #
        self.domain_service.recalculate_sheet_totals(sheet)
        
        return report
    # ========== 2. MASTER DATA (Config) ========== #
    def list_cost_types(self, user: User):
        """ لیست کردن انواع هزینه‌ها """
        AppPermissionChecker.check_has_permission(user, 'view_ordercostcategory')
        return OrderFinancialCategory.objects.get_all_active()

    def create_cost_type(self, user: User, data: dict):
        """ تعریف نوع هزینه جدید (مثلا: چسب صحافی) """
        AppPermissionChecker.check_has_permission(user, 'add_ordercostcategory')
        if OrderFinancialCategory.objects.get_by_slug(data.get('slug')):
             raise ValidationError("کد دسته‌بندی تکراری است.")

        category = OrderFinancialCategory.objects.create(**data)
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
            category = OrderFinancialCategory.objects.get(id=category_id)
        except OrderFinancialCategory.DoesNotExist:
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
            category = OrderFinancialCategory.objects.get(id=category_id)
        except OrderFinancialCategory.DoesNotExist:
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
        user_role_relation = user.user_role.first()

        if not user_role_relation:
             raise PermissionDenied("کاربر فاقد نقش سیستمی است.")
             
        user_role = user_role_relation.role
        
        print(f"Role Name: {user_role.name}")
        # ===== بررسی وضعیت فعلی سفارش ===== #
        current_status = order.current_status
        if not current_status or not current_status.group:
            raise PermissionDenied("وضعیت فعلی سفارش نامعتبر است.")

        current_group_code = current_status.group.code
        
        # ===== بررسی دسترسی کاربر به گروه وضعیت ===== #
        allowed_codes = list(user_role.allowed_groups.values_list('code', flat=True))
        print(allowed_codes)
        if current_group_code not in allowed_codes:
            self.audit_service.record_log(
                user=user,
                obj=order,
                action='SCOPE_ACCESS_DENIED',
                changes={
                    'current_stage': current_group_code,
                    'user_role': user_role.slug,
                    'allowed_stages': allowed_codes
                },
                description=_("تلاش غیرمجاز برای ثبت هزینه در مرحله غیرمرتبط")
            )
            raise PermissionDenied(
                f"نقش شما ({user_role.name}) مجاز به ثبت هزینه در مرحله '{current_status.group.name}' نیست."
            )
        
    def _ensure_sheet_exists(self, order_id: int) -> OrderFinancialSheet:
        """ اگر شیت وجود نداشت، یکی بساز """
        sheet = OrderFinancialSheet.objects.get_by_order_id(order_id)
        if not sheet:
            sheet = OrderFinancialSheet.objects.create(order_id=order_id)
        return sheet

    def _create_attachments(self, report: OrderFinancialReport, files: List[UploadedFile]):
        """Helper to create attachments"""
        attachments = []
        for file in files:
            OrderFinancialAttachment.objects.create(report=report, file=file, title=file.name)
