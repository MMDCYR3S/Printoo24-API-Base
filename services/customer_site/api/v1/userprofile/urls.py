from django.urls import path, include
from .views import (
    CustomerProfileAPIView,
    UserOrderListAPIView,
    UserOrderDetailAPIView,
    UserAddressListCreateAPIView,
    UserAddressDetailAPIView,
    WalletDetailAPIView,
    WalletHistoryAPIView
)

urlpatterns = [
    path('info/', CustomerProfileAPIView.as_view(), name='user-profile-detail'),
    # ===== بخش سابقه سفارشات ===== #
    path('orders/', UserOrderListAPIView.as_view(), name='user-order-list'),
    path('orders/<int:order_id>/', UserOrderDetailAPIView.as_view(), name='user-order-detail'),
    # ===== بخش آدرس ===== #
    path('addresses/', UserAddressListCreateAPIView.as_view(), name='user-address-list-create'),
    path('addresses/<int:address_id>/', UserAddressDetailAPIView.as_view(), name='user-address-detail'),
    # ===== بخش کیف پول ===== #
    path('wallet/', WalletDetailAPIView.as_view(), name='wallet-detail'),
    path('wallet/history/', WalletHistoryAPIView.as_view(), name='wallet-history'),
]
