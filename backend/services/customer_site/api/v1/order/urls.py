from django.urls import path, include

from .views import CreateOrderView

urlpatterns = [
    path("create/", CreateOrderView.as_view(), name="create_order")
]