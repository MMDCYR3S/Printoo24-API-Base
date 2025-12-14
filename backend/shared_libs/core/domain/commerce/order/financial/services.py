from decimal import Decimal
from typing import List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import Order, User, OrderCostSheet, OrderCostItem, OrderCostCategory, OrderCostAttachment
from .repositories import OrderCostSheetRepository, OrderCostItemRepository, OrderCostCategoryRepository

# ========== Order Cost Domain Service ========== #
class OrderCostDomainService:
    def __init__(self):
        self.type_repo = OrderCostCategoryRepository()
        self.report_repo = OrderCostSheetRepository()
        self.item_repo = OrderCostItemRepository()

    @transaction.atomic
    def create_cost_report(self, 
                           order: Order, 
                           user: User, 
                           title: str, 
                           description: str, 
                           items_data: List[Dict[str, Any]],
                           attachments_data: List[Any] = None) -> OrderCostSheet:
        """
        ایجاد گزارش هزینه به همراه اقلام و فایل‌های پیوست.
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
            amount = item.get('amount')
            desc = item.get('description', '')

            if not catalog_id and not custom_title:
                raise ValidationError(f"در ردیف {index+1}، باید یا یک کالا از لیست انتخاب کنید یا عنوان دستی وارد کنید.")

            # =====ایجاد آیتم هزینه ===== #
            cost_items_to_create.append(OrderCostItem(
                report=report,
                catalog_item_id=catalog_id,
                custom_title=custom_title if not catalog_id else None,
                amount=amount,
                description=desc
            ))
        
        # ===== 4. ثبت گروهی اقلام ===== #
        self.item_repo.bulk_create_items(cost_items_to_create)
        
        # ===== 5. ثبت پیوست ها ===== #
        if attachments_data:
            attachments_to_create = []
            for file in attachments_data:
                attachments_to_create.append(OrderCostAttachment(
                    report=report,
                    file=file,
                    title=file.name
                ))
            OrderCostAttachment.objects.bulk_create(attachments_to_create)
        
        return report
    
    @transaction.atomic
    def update_cost_report_header(self, report_id: int, user: User, data: Dict[str, Any]) -> OrderCostSheet:
        """ ویرایش اطلاعات کلی گزارش (عنوان، توضیحات، فایل) """
        report = self.report_repo.get_by_id(report_id)
        if not report:
            raise ValidationError("گزارش هزینه یافت نشد.")
        
        if report.is_approved_by_finance:
            raise ValidationError("این گزارش توسط مالی تایید شده و قابل ویرایش نیست.")
        
        update_fields = {}
        if 'title' in data: update_fields['title'] = data['title']
        if 'description' in data: update_fields['description'] = data['description']
        if 'attachment' in data:
            update_fields['attachment'] = data['attachment']
        else:
            pass
        
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
    def approve_cost_report(self, report_id: int, user: User, approved: bool = True) -> OrderCostSheet:
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
    
    # ========== Order Cost Type ========== #
    @transaction.atomic
    def create_cost_type(self, user: User, data: dict) -> OrderCostCategory:
        """ ایجاد یک نوع هزینه جدید """
        if self.type_repo.model.objects.filter(code=data['code']).exists():
            raise ValidationError("نوع هزینه با این کد سیستمی قبلاً تعریف شده است.")

        return self.type_repo.create({
            "title": data['title'],
            "code": data['code'],
            "category": data['category'],
            "is_deduction": data.get('is_deduction', False)
        })
    
    @transaction.atomic
    def update_cost_type(self, type_id: int, user: User, data: dict) -> OrderCostCategory:
        """ ویرایش نوع هزینه """
        cost_type = self.type_repo.get_by_id(type_id)
        if not cost_type:
            raise ValidationError("نوع هزینه یافت نشد.")
        return self.type_repo.update(cost_type, data)
    
    @transaction.atomic
    def delete_cost_type(self, type_id: int, user: User):
        """ حذف نوع هزینه (با بررسی وابستگی) """
        cost_type = self.type_repo.get_by_id(type_id)
        if not cost_type:
            raise ValidationError("نوع هزینه یافت نشد.")
        if hasattr(cost_type, 'ordercostcatalog_set') and cost_type.ordercostcatalog_set.exists():
             raise ValidationError("این نوع هزینه در کاتالوگ‌ها استفاده شده و قابل حذف نیست.")
        cost_type.delete()
