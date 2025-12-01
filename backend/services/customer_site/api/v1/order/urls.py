from django.urls import path, include

from .views import CreateOrderView

urlpatterns = [
    path("checkout/", CreateOrderView.as_view(), name="checkout")
]