from django.contrib import admin

from core.models import (
    Order,
    OrderItem,
    OrderItemFile,
    OrderStatus,
    OrderStatusGroup,
)

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderStatus)
admin.site.register(OrderItemFile)
admin.site.register(OrderStatusGroup)
