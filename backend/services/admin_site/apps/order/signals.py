from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderCostReport, OrderCostItem


# ========== محاسبه قیمت سند مالی ========== #
@receiver(post_save, sender=OrderCostReport)
def update_sheet_on_report_change(sender, instance, created, **kwargs):
    """
    هرگاه گزارشی ذخیره شد (چه جدید، چه آپدیت وضعیت)،
    سند مادر (Sheet) باید دوباره محاسبه شود.
    """
    if instance.sheet:
        instance.sheet.recalculate_totals()

@receiver(post_delete, sender=OrderCostReport)
def update_sheet_on_report_delete(sender, instance, **kwargs):
    """
    اگر گزارشی حذف شد، مبالغ آن باید از سند مادر کسر شود.
    """
    if instance.sheet:
        instance.sheet.recalculate_totals()

@receiver(post_save, sender=OrderCostItem)
def update_sheet_on_item_change(sender, instance, created, **kwargs):
    """
    اگر مبلغ ریز اقلام تغییر کرد، باید روی ریپورت و سپس روی شیت تاثیر بگذارد.
    """
    if instance.report and instance.report.sheet:
        instance.report.sheet.recalculate_totals()
