from django.contrib import admin
from core.models import OrderShipment, DeliveryMethod, OrderPackage

admin.site.register(OrderShipment)
admin.site.register(DeliveryMethod)
admin.site.register(OrderPackage)
