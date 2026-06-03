from typing import Optional
from django.db import models
from .base import BaseQuerySet
from django.db import models
from django.db.models import Sum, Count, Avg

# ========== INVOICE QUERYSET ========== #
class InvoiceQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به فاکتور"""
    
    def get_invoice_by_order(self, order_id: int):
        """ دریافت فاکتور مرتبط با یک سفارش خاص """
        return self.select_related('order__user').filter(order_id=order_id).first()

    def get_invoices_with_details(self):
        """ لیست فاکتورها برای پنل مدیریت (همراه با سفارش و کاربر) """
        return self.select_related(
            'order__user__customer_profile'
        ).order_by('-issued_at')
        
    def get_invoice_detail(self, invoice_id: int):
        """ دریافت جزئیات کامل یک فاکتور """
        return self.select_related(
            'order__user', 'order__address'
        ).filter(id=invoice_id).first()
    
    def get_by_invoice_number(self, number: str):
        return self.filter(invoice_number=number).first()
    
    def active(self):
        """ فاکتورهای غیر لغو — پایه تمام محاسبات مالی """
        return self.exclude(status='CANCELED')

    def get_total_revenue(self) -> int:
        """ کل مبلغ صادرشده (final_amount) بدون لغوشده‌ها """
        result = self.active().aggregate(total=Sum('final_amount'))
        return int(result['total'] or 0)

    def get_total_paid(self) -> int:
        """ کل مبلغ واقعاً دریافت‌شده (paid_amount) بدون لغوشده‌ها """
        result = self.active().aggregate(total=Sum('paid_amount'))
        return int(result['total'] or 0)

    def get_revenue_by_date_range(self, start_date, end_date) -> int:
        result = self.active().filter(
            issued_at__range=(start_date, end_date)
        ).aggregate(total=Sum('final_amount'))
        return int(result['total'] or 0)

    def get_paid_by_date_range(self, start_date, end_date) -> int:
        result = self.active().filter(
            issued_at__range=(start_date, end_date)
        ).aggregate(total=Sum('paid_amount'))
        return int(result['total'] or 0)

    def get_average_invoice_value(self) -> int:
        result = self.active().aggregate(avg=Avg('final_amount'))
        return int(result['avg'] or 0)

    def get_daily_revenue_chart_data(self, days: int = 30):
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models.functions import TruncDay

        start_date = timezone.now() - timedelta(days=days)
        chart_data = self.active()\
            .filter(issued_at__gte=start_date)\
            .annotate(date=TruncDay('issued_at'))\
            .values('date')\
            .annotate(total=Sum('final_amount'), paid=Sum('paid_amount'), count=Count('id'))\
            .order_by('date')
        return list(chart_data)

    def get_status_breakdown(self):
        return self.values('status').annotate(
            count=Count('id'),
            total=Sum('final_amount')
        ).order_by('-count')

# ========== INVOICE MANAGER ========== #
class InvoiceManager(models.Manager):
    def get_queryset(self):
        return InvoiceQuerySet(self.model, using=self._db)

    def get_invoice_by_order(self, order_id: int):
        return self.get_queryset().get_invoice_by_order(order_id)

    def get_invoices_with_details(self):
        return self.get_queryset().get_invoices_with_details()

    def get_invoice_detail(self, invoice_id: int):
        return self.get_queryset().get_invoice_detail(invoice_id)
    
    def get_by_invoice_number(self, number: str):
        return self.get_queryset().get_by_invoice_number(number)
    
    def create_invoice(self, data):
        return self.create(**data)
    
    def get_queryset(self):
        return InvoiceQuerySet(self.model, using=self._db)

    def get_total_revenue(self):
        return self.get_queryset().get_total_revenue()

    def get_total_paid(self):
        return self.get_queryset().get_total_paid()

    def get_revenue_by_date_range(self, start, end):
        return self.get_queryset().get_revenue_by_date_range(start, end)

    def get_paid_by_date_range(self, start, end):
        return self.get_queryset().get_paid_by_date_range(start, end)

    def get_average_invoice_value(self):
        return self.get_queryset().get_average_invoice_value()

    def get_daily_revenue_chart_data(self, days=30):
        return self.get_queryset().get_daily_revenue_chart_data(days)

    def get_status_breakdown(self):
        return self.get_queryset().get_status_breakdown()