from django.contrib import admin
from apps.cart.models import CartItem, Cart

# Register your models here.
admin.site.register(CartItem)
admin.site.register(Cart)