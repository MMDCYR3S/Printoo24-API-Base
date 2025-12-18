from django.contrib import admin
from core.models import OrderShipment, OrderPackage
from core.site import custom_admin_site

custom_admin_site.register(OrderShipment)
custom_admin_site.register(OrderPackage)
