from django.contrib import admin

from core.models import Product, OrderStateLog
from core.site import custom_admin_site
from apps.order.models import *

custom_admin_site.register(Product)
custom_admin_site.register(OrderFinancialItem)
custom_admin_site.register(OrderFinancialCategory)
custom_admin_site.register(OrderFinancialSheet)
custom_admin_site.register(OrderStateLog)
