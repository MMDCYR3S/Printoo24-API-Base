from typing import Any, Dict
from rest_framework.exceptions import NotFound, ValidationError

from core.financial.models import Quotation
from core.financial.services import QuotationService


class QuotationDashboardService:
    """
    سرویس مدیریت پیش‌فاکتورها در داشبورد ادمین
    """

    def __init__(self):
        self.domain = QuotationService()

    def get_quotation_list(self):
        return Quotation.objects.select_related(
            'created_by', 'converted_order', 'cart_item__cart'
        ).all().order_by('-created_at')

    def get_quotation_detail(self, quotation_id: int) -> Quotation:
        try:
            return Quotation.objects.select_related(
                'created_by', 'converted_order', 'cart_item__cart'
            ).get(pk=quotation_id)
        except Quotation.DoesNotExist:
            raise NotFound("پیش‌فاکتور مورد نظر یافت نشد.")

    def create_quotation(self, data: Dict[str, Any], actor) -> Quotation:
        order_id = data.get('order_id')
        if not order_id:
            raise ValidationError("order_id الزامی است.")
        return self.domain.create_quotation(order_id, data, actor)

    def update_quotation(self, quotation_id: int, data: Dict[str, Any]) -> Quotation:
        return self.domain.update_quotation(quotation_id, data)

    def delete_quotation(self, quotation_id: int):
        return self.domain.delete_quotation(quotation_id)

    def approve_quotation(self, quotation_id: int) -> Quotation:
        return self.domain.approve_quotation(quotation_id)

    def change_status(self, quotation_id: int, new_status: str) -> Quotation:
        return self.domain.change_status(quotation_id, new_status)