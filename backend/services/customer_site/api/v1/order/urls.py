from django.urls import path, include

from .views import CreateOrderView

urlpatterns = [
    path("checkout/<int:item_id>/", CreateOrderView.as_view(), name="checkout")
]