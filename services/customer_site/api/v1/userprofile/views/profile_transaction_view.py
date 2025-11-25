from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.views import extend_schema

from apps.userprofile.services import WalletService
from ..serializers import WalletSerializer, WalletTransactionSerializer

# ===== Wallet Detail API View ===== #
@extend_schema(tags=["Profile"])
class WalletDetailAPIView(APIView):
    """نمایش موجودی کیف پول کاربر"""
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = WalletService()

    def get(self, request):
        wallet = self.service.get_wallet_balance(request.user.id)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

# ===== Wallet History APIView ===== #
@extend_schema(tags=["Profile"])
class WalletHistoryAPIView(APIView):
    """نمایش لیست تراکنش‌های کاربر"""
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = WalletService()

    def get(self, request):
        transactions = self.service.get_transaction_history(request.user.id)
        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
