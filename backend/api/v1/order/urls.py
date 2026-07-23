from django.urls import path

from .views import CreateOrderView, BulkCreateOrderView, UserAddressListView, ProvinceView, CityView

urlpatterns = [
    path("checkout/<int:item_id>/", CreateOrderView.as_view(), name="checkout"),
    path('checkout/all/', BulkCreateOrderView.as_view(), name='checkout-bulk'),
    path('addresses/', UserAddressListView.as_view(), name='user-addresses'),
    path('provinces/', ProvinceView.as_view(), name='province-list'),
    path('cities/', CityView.as_view(), name='city-list'),
]