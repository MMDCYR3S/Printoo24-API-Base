from django.contrib import admin

from core.models import (
    Order,
    OrderItem,
    OrderItemDesignFile,
    DesignFile,
    OrderStatus,
)

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderItemDesignFile)
admin.site.register(DesignFile)
admin.site.register(OrderStatus)
