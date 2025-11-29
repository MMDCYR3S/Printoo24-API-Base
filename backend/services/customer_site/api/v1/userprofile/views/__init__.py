from .profile_detail_view import CustomerProfileAPIView 
from .profile_order_view import (
    UserOrderDetailAPIView,
    UserOrderListAPIView
)
from .profile_address_view import (
    UserAddressDetailAPIView,
    UserAddressListCreateAPIView
)
from .profile_transaction_view import (
    WalletDetailAPIView,
    WalletHistoryAPIView
)