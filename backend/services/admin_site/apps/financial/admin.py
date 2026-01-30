from django.contrib import admin
from core.models import (
    Invoice, Quotation
)
from core.site import custom_admin_site
from apps.order.models import OrderCostReport, OrderCostAttachment, OrderCostType
from .models import Transaction

custom_admin_site.register(Transaction)
custom_admin_site.register(Invoice)
custom_admin_site.register(Quotation)
custom_admin_site.register(OrderCostReport)
custom_admin_site.register(OrderCostAttachment)
custom_admin_site.register(OrderCostType)


