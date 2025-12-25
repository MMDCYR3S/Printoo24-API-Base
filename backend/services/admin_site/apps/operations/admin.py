from django.contrib import admin

from core.models import Product
from core.site import custom_admin_site
from apps.order.models import *

custom_admin_site.register(Product)
custom_admin_site.register(OrderCostItem)
custom_admin_site.register(OrderCostCategory)
custom_admin_site.register(OrderCostSheet)
