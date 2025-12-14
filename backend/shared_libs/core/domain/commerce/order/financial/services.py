from decimal import Decimal
from typing import List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import (
    Order, User, OrderCostSheet, OrderCostReport, 
    OrderCostItem, OrderCostCategory, OrderCostAttachment
)
from .repositories import (
    OrderCostSheetRepository, OrderCostReportRepository, 
    OrderCostItemRepository, OrderCostCategoryRepository,
    OrderCostAttachmentRepository
)

# ============ ORDER COST DOMAIN SERVICE ============ #
class OrderCostDomainService:
    def __init__(self):
        self.sheet_repo = OrderCostSheetRepository()
        self.report_repo = OrderCostReportRepository()
        self.item_repo = OrderCostItemRepository()
        self.attachment_repo = OrderCostAttachmentRepository()
        self.category_repo = OrderCostCategoryRepository()

    # ============ REPORT CRUD OPERATIONS ============ #
    @transaction.atomic
    def submit_cost_report(self, 
                           order_id: int, 
                           user: User, 
                           department: str, 
                           cost_type: str, 
                           title: str,
                           items_data: List[Dict[str, Any]], 
                           attachments_data: List[Any] = None,
                           description: str = "") -> OrderCostReport:
        """
        ایجاد و ارسال یک گزارش هزینه جدید (CREATE Report).
        """
        # 1. دریافت یا ایجاد سند مادر (Ledger)
        sheet = self.sheet_repo.get_by_order_id(order_id)
        if not sheet:
            try:
                order = Order.objects.get(id=order_id)
                sheet = OrderCostSheet.objects.create(order=order)
            except Order.DoesNotExist:
                raise ValidationError("سفارش مورد نظر یافت نشد.")
            
        if sheet.is_locked:
            raise ValidationError("سند مالی این سفارش قفل شده است.")

        # 2. ایجاد هدر گزارش
        report = self.report_repo.create({
            "sheet": sheet,
            "submitter": user,
            "department": department,
            "cost_type": cost_type,
            "title": title,
            "description": description,
            "is_approved": False
        })

        # 3. افزودن اقلام
        self._process_and_add_items(report, items_data)

        # 4. افزودن پیوست‌ها
        if attachments_data:
            self._add_attachments(report, attachments_data)

        return report

    @transaction.atomic
    def update_cost_report(self, report_id: int, user: User, data: Dict[str, Any]) -> OrderCostReport:
        """
        ویرایش گزارش هزینه (UPDATE Report).
        فقط گزارش‌های تایید نشده قابل ویرایش هستند.
        """
        report = self.report_repo.get_by_id(report_id)
        if not report: raise ValidationError("گزارش یافت نشد.")
        
        if report.is_approved:
            raise ValidationError("گزارش تایید شده و قابل ویرایش نیست.")
            
        if report.submitter != user and not user.is_superuser:
             raise ValidationError("شما فقط می‌توانید گزارش‌های خودتان را ویرایش کنید.")

        # آپدیت فیلدها
        if 'title' in data: report.title = data['title']
        if 'description' in data: report.description = data['description']
        if 'department' in data: report.department = data['department']
        if 'cost_type' in data: report.cost_type = data['cost_type']
        
        report.save()
        return report

    @transaction.atomic
    def delete_cost_report(self, report_id: int, user: User):
        """
        حذف گزارش هزینه (DELETE Report).
        """
        report = self.report_repo.get_by_id(report_id)
        if not report: raise ValidationError("گزارش یافت نشد.")
        
        if report.is_approved:
            # اگر تایید شده باشد، حذف آن باعث بهم ریختن محاسبات می‌شود
            # مگر اینکه لاجیک Revert را داشته باشیم (که با سیگنال هندل می‌شود)
            # اما معمولاً گزارش مالی تایید شده پاک نمی‌شود.
            raise ValidationError("گزارش تایید شده قابل حذف نیست (باید توسط مالی رد شود).")
            
        if report.submitter != user and not user.is_superuser:
             raise ValidationError("شما اجازه حذف این گزارش را ندارید.")
             
        report.delete()

    # ============ ITEM CRUD OPERATIONS ============ #
    @transaction.atomic
    def add_item_to_report(self, report_id: int, item_data: Dict[str, Any]) -> OrderCostItem:
        """ افزودن یک قلم به گزارش موجود """
        report = self.report_repo.get_by_id(report_id)
        if not report: raise ValidationError("گزارش یافت نشد.")
        if report.is_approved: raise ValidationError("گزارش تایید شده است.")

        amount = Decimal(str(item_data.get('amount', 0)))
        if amount <= 0: raise ValidationError("مبلغ نامعتبر است.")

        category = None
        if item_data.get('category_id'):
            category = self.category_repo.get_by_id(item_data['category_id'])

        return self.item_repo.create({
            "report": report,
            "catalog_item": category,
            "custom_title": item_data.get('custom_title'),
            "quantity": item_data.get('quantity', 1),
            "amount": amount,
            "description": item_data.get('description', '')
        })

    @transaction.atomic
    def update_cost_item(self, item_id: int, data: Dict[str, Any]) -> OrderCostItem:
        """ ویرایش قلم هزینه """
        item = self.item_repo.get_by_id(item_id)
        if not item: raise ValidationError("قلم هزینه یافت نشد.")
        if item.report.is_approved: raise ValidationError("گزارش تایید شده است.")

        if 'amount' in data:
            amount = Decimal(str(data['amount']))
            if amount <= 0: raise ValidationError("مبلغ نامعتبر است.")
            item.amount = amount
            
        if 'custom_title' in data: item.custom_title = data['custom_title']
        if 'quantity' in data: item.quantity = data['quantity']
        if 'description' in data: item.description = data['description']
        
        item.save()
        return item

    @transaction.atomic
    def delete_cost_item(self, item_id: int):
        """ حذف قلم هزینه """
        item = self.item_repo.get_by_id(item_id)
        if not item: raise ValidationError("قلم هزینه یافت نشد.")
        if item.report.is_approved: raise ValidationError("گزارش تایید شده است.")
        
        if item.report.items.count() <= 1:
             raise ValidationError("نمی‌توانید آخرین قلم گزارش را حذف کنید. کل گزارش را حذف کنید.")
             
        item.delete()

    # ============ ATTACHMENT CRUD ============ #
    @transaction.atomic
    def add_attachment(self, report_id: int, file) -> OrderCostAttachment:
        """ افزودن پیوست به گزارش """
        report = self.report_repo.get_by_id(report_id)
        if not report: raise ValidationError("گزارش یافت نشد.")
        
        return self.attachment_repo.create({
            "report": report,
            "file": file,
            "title": file.name
        })

    def delete_attachment(self, attachment_id: int):
        """ حذف پیوست """
        att = self.attachment_repo.get_by_id(attachment_id)
        if not att: raise ValidationError("پیوست یافت نشد.")
        if att.report.is_approved: raise ValidationError("گزارش تایید شده است.")
        att.delete()


    # ============ APPROVAL LOGIC ============ #
    @transaction.atomic
    def approve_report(self, report_id: int, approver: User) -> OrderCostReport:
        """ تایید گزارش (Financial Approval) """
        report = self.report_repo.get_report_detail(report_id)
        if not report: raise ValidationError("گزارش یافت نشد.")
        if report.sheet.is_locked: raise ValidationError("سند مادر قفل شده است.")
        if report.is_approved: raise ValidationError("قبلاً تایید شده است.")

        report.is_approved = True
        report.save() 
        return report

    @transaction.atomic
    def reject_report(self, report_id: int, user: User) -> OrderCostReport:
        """ رد گزارش """
        report = self.report_repo.get_report_detail(report_id)
        if not report: raise ValidationError("گزارش یافت نشد.")

        report.is_approved = False
        report.save()
        return report

    # ============ SHEET (READ ONLY) ============ #
    def get_order_financial_summary(self, order_id: int) -> dict:
        sheet = self.sheet_repo.get_by_order_id(order_id)
        if not sheet: return {}
        return {
            "total_material": sheet.total_material_cost,
            "total_service": sheet.total_service_cost,
            "total_shipping": sheet.total_shipping_cost,
            "total_overhead": sheet.total_overhead_cost,
            "final_cost": sheet.final_total_cost,
            "revenue": sheet.revenue_amount,
            "net_profit": sheet.net_profit,
            "margin_percent": sheet.profit_margin_percent,
            "is_locked": sheet.is_locked
        }

    @transaction.atomic
    def lock_cost_sheet(self, order_id: int, user: User) -> OrderCostSheet:
        sheet = self.sheet_repo.get_by_order_id(order_id)
        if not sheet: raise ValidationError("سند یافت نشد.")
        sheet.recalculate_totals()
        sheet.is_locked = True
        sheet.save()
        return sheet

    # ============ CATEGORY CRUD ============ #
    def create_category(self, data: dict) -> OrderCostCategory:
        if self.category_repo.model.objects.filter(slug=data['slug']).exists():
            raise ValidationError("کد دسته‌بندی تکراری است.")
        return self.category_repo.create(data)

    def update_category(self, category_id: int, data: dict) -> OrderCostCategory:
        if 'slug' in data:
            if self.category_repo.model.objects.filter(slug=data['slug']).exclude(id=category_id).exists():
                raise ValidationError("کد دسته‌بندی تکراری است.")
        return self.category_repo.update(category_id, data)

    def delete_category(self, user: User, category_id: int):
        if OrderCostItem.objects.filter(catalog_item_id=category_id).exists():
             raise ValidationError("این دسته‌بندی استفاده شده است.")
        self.category_repo.delete(category_id)

    def get_all_categories(self):
        return self.category_repo.get_all_active()

    # ===== Internal Helpers ===== #
    def _process_and_add_items(self, report, items_data):
        new_items = []
        for index, item_data in enumerate(items_data):
            amount = Decimal(str(item_data.get('amount', 0)))
            if amount <= 0: raise ValidationError(f"مبلغ ردیف {index+1} نامعتبر است.")

            category = None
            if item_data.get('category_id'):
                category = self.category_repo.get_by_id(item_data['category_id'])

            new_items.append(OrderCostItem(
                report=report,
                catalog_item=category,
                custom_title=item_data.get('custom_title'),
                quantity=item_data.get('quantity', 1),
                amount=amount,
                description=item_data.get('description', '')
            ))
        
        if new_items:
            self.item_repo.bulk_create_items(new_items)
        else:
            raise ValidationError("حداقل یک آیتم الزامی است.")

    def _add_attachments(self, report, attachments_data):
        attachments = [
            OrderCostAttachment(report=report, file=f, title=f.name) 
            for f in attachments_data
        ]
        self.attachment_repo.bulk_create_attachments(attachments)
