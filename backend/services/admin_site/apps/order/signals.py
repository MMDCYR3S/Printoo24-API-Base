from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderFinancialReport, OrderFinancialItem, OrderFinancialSheet
from apps.logistics.models import OrderShipment
from core.models import Order


# ========== محاسبه قیمت سند مالی ========== #
@receiver(post_save, sender=OrderFinancialReport)
def update_sheet_on_report_change(sender, instance, created, **kwargs):
    """
    هرگاه گزارشی ذخیره شد (چه جدید، چه آپدیت وضعیت)،
    سند مادر (Sheet) باید دوباره محاسبه شود.
    """
    if instance.sheet:
        instance.sheet.recalculate_totals()

@receiver(post_delete, sender=OrderFinancialReport)
def update_sheet_on_report_delete(sender, instance, **kwargs):
    """
    اگر گزارشی حذف شد، مبالغ آن باید از سند مادر کسر شود.
    """
    if instance.sheet:
        instance.sheet.recalculate_totals()

@receiver(post_save, sender=OrderFinancialItem)
def update_sheet_on_item_change(sender, instance, created, **kwargs):
    """
    اگر مبلغ ریز اقلام تغییر کرد، باید روی ریپورت و سپس روی شیت تاثیر بگذارد.
    """
    if instance.report and instance.report.sheet:
        instance.report.sheet.recalculate_totals()

# ========== بخش مربوط به ایجاد زمان تحویل سفارش ========== #
@receiver(post_save, sender=Order)
def create_shipment_informations(sender, instance,  created, **kwargs):
    """
    ایجاد یک بخش برای بسته‌بندی و تحویل و حمل‌ونقل برای سفارش
    """
    if created:
        OrderShipment.objects.create(
            order=instance,
            destination_address=instance.full_address,
            tracking_code=instance.order_code,
            status="processing"
        )

@receiver(post_save, sender=Order)
def create_financial_sheet(sender, instance, created, **kwargs):
    """
    ایجاد یک سند مالی برای هر سفارش جدید
    """
    if created:
        OrderFinancialSheet.objects.create(
            order=instance,
            total_revenue=instance.total_price
        )
