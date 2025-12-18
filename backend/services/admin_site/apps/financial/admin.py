from django.contrib import admin
from core.models import (
    Transaction, Invoice, Quotation,
    OrderCostReport, OrderCostAttachment, AuditLog
)
from core.site import custom_admin_site

custom_admin_site.register(Transaction)
custom_admin_site.register(Invoice)
custom_admin_site.register(Quotation)
custom_admin_site.register(OrderCostReport)
custom_admin_site.register(OrderCostAttachment)
custom_admin_site.register(AuditLog)


