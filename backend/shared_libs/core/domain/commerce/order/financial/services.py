from decimal import Decimal
from typing import List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import Order, User, OrderCostReport, OrderCostItem
from .repositories import OrderCostReportRepository, OrderCostItemRepository

# ========== Order Cost Domain Service ========== #
class OrderCostDomainService:
    def __init__(self):
        self.report_repo = OrderCostReportRepository()
        self.item_repo = OrderCostItemRepository()

    @transaction.atomic
    def create_cost_report(self, 
                           order: Order, 
                           user: User, 
                           title: str, 
                           description: str, 
                           attachment, 
                           items_data: List[Dict[str, Any]]) -> OrderCostReport:
        """
        ایجاد یک گزارش مالی کامل شامل هدر و اقلام ریز هزینه.
        قوانین دامین:
        1. گزارش بدون آیتم معنی ندارد.
        2. مبلغ هر آیتم باید مثبت باشد.
        3. هر آیتم باید یا Catalog ID داشته باشد یا Custom Title.
        """
        
        # ===== 1. اعتبارسنجی اقلام ===== #
        if not items_data:
            raise ValidationError("گزارش هزینه باید حداقل شامل یک قلم باشد.")

        # ===== 2. ایجاد هدر گزارش ===== #
        report = self.report_repo.create({
            "order": order,
            "created_by": user,
            "title": title,
            "description": description,
            "attachment": attachment,
            "is_approved_by_finance": False
        })

        # ===== 3. ایجاد اقلام ریز هزینه ===== #
        cost_items_to_create = []
        
        for index, item in enumerate(items_data):
            # ===== اعتبارسنجی مبلغ ===== #
            try:
                amount = Decimal(str(item.get('amount', 0)))
            except:
                raise ValidationError(f"مبلغ وارد شده در ردیف {index+1} نامعتبر است.")

            if amount <= 0:
                raise ValidationError(f"مبلغ هزینه در ردیف {index+1} باید بزرگتر از صفر باشد.")

            catalog_id = item.get('catalog_id')
            custom_title = item.get('custom_title')

            if not catalog_id and not custom_title:
                raise ValidationError(f"در ردیف {index+1}، باید یا یک کالا از لیست انتخاب کنید یا عنوان دستی وارد کنید.")

            # =====ایجاد آیتم هزینه ===== #
            cost_items_to_create.append(OrderCostItem(
                report=report,
                catalog_item_id=catalog_id,
                custom_title=custom_title if not catalog_id else None,
                amount=amount,
                description=item.get('description', '')
            ))
        
        # ===== 4. ثبت گروهی اقلام ===== #
        self.item_repo.bulk_create_items(cost_items_to_create)
        
        return report
    
    @transaction.atomic
    def update_cost_report_header(self, report_id: int, user: User, data: Dict[str, Any]) -> OrderCostReport:
        """ ویرایش اطلاعات کلی گزارش (عنوان، توضیحات، فایل) """
        report = self.report_repo.get_by_id(report_id)
        if not report:
            raise ValidationError("گزارش هزینه یافت نشد.")
        
        if report.is_approved_by_finance:
            raise ValidationError("این گزارش توسط مالی تایید شده و قابل ویرایش نیست.")
        
        update_fields = {}
        if 'title' in data: update_fields['title'] = data['title']
        if 'description' in data: update_fields['description'] = data['description']
        if 'attachment' in data: update_fields['attachment'] = data['attachment']
        
        return self.report_repo.update(report, update_fields)
    
    @transaction.atomic
    def update_cost_item(self, item_id: int, user: User, data: Dict[str, Any]) -> OrderCostItem:
        """ ویرایش یک قلم هزینه خاص """
        item = self.item_repo.get_by_id(item_id)
        if not item:
            raise ValidationError("قلم هزینه یافت نشد.")
        
        if item.report.is_approved_by_finance:
            raise ValidationError("گزارش مربوطه تایید شده و اقلام آن قابل تغییر نیستند.")
        
        if 'amount' in data:
            new_amount = Decimal(str(data['amount']))
            if new_amount <= 0:
                raise ValidationError("مبلغ باید مثبت باشد.")
            item.amount = new_amount
            
        if 'description' in data:
            item.description = data['description']
            
        item.save()
        return item
    
    @transaction.atomic
    def delete_cost_report(self, report_id: int, user: User):
        """ حذف کل گزارش هزینه """
        report = self.report_repo.get_by_id(report_id)
        if not report:
            raise ValidationError("گزارش هزینه یافت نشد.")
        
        if report.is_approved_by_finance:
            raise ValidationError("امکان حذف گزارش تایید شده وجود ندارد. ابتدا تایید را لغو کنید.")
            
        report.delete()
        
    @transaction.atomic
    def delete_cost_item(self, item_id: int, user: User):
        """ حذف یک قلم از گزارش """
        item = self.item_repo.get_by_id(item_id)
        if not item:
            raise ValidationError("قلم هزینه یافت نشد.")
        
        if item.report.is_approved_by_finance:
            raise ValidationError("گزارش تایید شده است.")
        
        item.delete()
        
    @transaction.atomic
    def approve_cost_report(self, report_id: int, user: User, approved: bool = True) -> OrderCostReport:
        """ 
        تایید یا رد نهایی گزارش توسط مدیر مالی.
        وقتی تایید شود، مبلغ آن باید روی فاکتور نهایی اعمال شود (در آینده).
        """
        
        report = self.report_repo.get_by_id(report_id)
        if not report:
            raise ValidationError("گزارش یافت نشد.")

        report.is_approved_by_finance = approved
        if approved:
            report.finance_note = f"توسط {user.username} تایید شد."
        
        report.save()
        return report
    