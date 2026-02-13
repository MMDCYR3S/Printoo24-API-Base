from django.contrib import admin
from core.models import (
    Invoice, Quotation
)
from core.site import custom_admin_site
from apps.order.models import OrderFinancialReport, OrderFinancialAttachment, OrderFinancialType, OrderFinancialCategory
from .models import Transaction

custom_admin_site.register(Transaction)
custom_admin_site.register(Invoice)
custom_admin_site.register(Quotation)
custom_admin_site.register(OrderFinancialReport)
custom_admin_site.register(OrderFinancialAttachment)
custom_admin_site.register(OrderFinancialType)


