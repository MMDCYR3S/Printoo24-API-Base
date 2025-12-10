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
    