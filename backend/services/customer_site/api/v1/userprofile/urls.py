from django.urls import path, include
from .views import (
    CustomerProfileAPIView,
    UserCommentListView,
    UserOrderListAPIView,
    UserOrderDetailAPIView,
    UserAddressListCreateAPIView,
    UserAddressDetailAPIView,
    WalletDetailAPIView,
    WalletHistoryAPIView,
    UserOrderQuotationAPIView,
    ProvinceListAPIView,
    CityListAPIView,
    UserOrderInvoiceAPIView,
)

urlpatterns = [
    path('info/', CustomerProfileAPIView.as_view(), name='user-profile-detail'),
    path('comments/', UserCommentListView.as_view(), name='profile-comments'),
    # ===== بخش سابقه سفارشات ===== #
    path('orders/', UserOrderListAPIView.as_view(), name='user-order-list'),
    path('orders/<int:order_id>/', UserOrderDetailAPIView.as_view(), name='user-order-detail'),
    path("orders/quotation/<int:order_id>/", UserOrderQuotationAPIView.as_view(), name="user-order-quotation"),
    path("orders/invoice/<int:order_id>/", UserOrderInvoiceAPIView.as_view(), name="user-order-invoice"),
    # ===== بخش آدرس ===== #
    path('addresses/', UserAddressListCreateAPIView.as_view(), name='user-address-list-create'),
    path('addresses/<int:address_id>/', UserAddressDetailAPIView.as_view(), name='user-address-detail'),
    # ===== بخش کیف پول ===== #
    path('wallet/', WalletDetailAPIView.as_view(), name='wallet-detail'),
    path('wallet/history/', WalletHistoryAPIView.as_view(), name='wallet-history'),
    # ===== نمایش استان و شهر ===== #
    path('locations/provinces/', ProvinceListAPIView.as_view(), name='location-provinces'),
    path('locations/cities/', CityListAPIView.as_view(), name='location-cities'),
]