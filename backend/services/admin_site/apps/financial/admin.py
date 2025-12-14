from django.contrib import admin
from core.models import (
    Transaction, Invoice, Quotation,
    OrderCostReport, OrderCostAttachment, InvoiceStatus
)

admin.site.register(Transaction)
admin.site.register(Invoice)
admin.site.register(Quotation)
admin.site.register(OrderCostReport)
admin.site.register(OrderCostAttachment)
admin.site.register(InvoiceStatus)
