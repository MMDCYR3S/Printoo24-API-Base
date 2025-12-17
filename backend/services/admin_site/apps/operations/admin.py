from django.contrib import admin
from core.models import Product, OrderCostItem, OrderCostCategory, OrderCostSheet, OrderStateLog
# Register your models here.

admin.site.register(Product)
admin.site.register(OrderCostItem)
admin.site.register(OrderCostCategory)
admin.site.register(OrderCostSheet)
admin.site.register(OrderStateLog)
