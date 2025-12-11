from django.contrib import admin
from core.models import Product, OrderCostItem, OrderCostReport, OrderCostCatalog, OrderCostType, OrderStateLog
# Register your models here.

admin.site.register(Product)
admin.site.register(OrderCostItem)
admin.site.register(OrderCostReport)
admin.site.register(OrderCostCatalog)
admin.site.register(OrderCostType)
admin.site.register(OrderStateLog)
