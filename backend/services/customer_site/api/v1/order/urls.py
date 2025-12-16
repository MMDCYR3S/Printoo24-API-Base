from django.urls import path

from .views import CreateOrderView, BulkCreateOrderView

urlpatterns = [
    path("checkout/<int:item_id>/", CreateOrderView.as_view(), name="checkout"),
    path('checkout/all/', BulkCreateOrderView.as_view(), name='checkout-bulk'),
]