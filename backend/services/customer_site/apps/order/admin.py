from django.contrib import admin

from core.models import (
    Order,
    OrderItem,
    OrderItemFile,
    OrderStatus
)

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderStatus)
admin.site.register(OrderItemFile)
