from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.userprofile.services import WalletAppService
from ..serializers import WalletSerializer, WalletTransactionSerializer


@extend_schema(tags=["Profile - Wallet"])
class WalletViewSet(viewsets.ViewSet):
    """
    کیف پول کاربر عادی (مشاهده موجودی و تاریخچه تراکنش‌ها)
    """
    permission_classes = [IsAuthenticated]

    def _get_service(self):
        """ساخت سرویس با کاربر جاری"""
        return WalletAppService(user=self.request.user)

    @extend_schema(
        summary="مشاهده موجودی و آمار کیف پول",
        responses={200: WalletSerializer},
    )
    @action(detail=False, methods=['get'], url_path='balance')
    def balance(self, request):
        service = self._get_service()
        wallet = service.get_wallet_balance(request.user.id)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

    @extend_schema(
        summary="تاریخچه تراکنش‌های کیف پول",
        responses={200: WalletTransactionSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='transactions')
    def transactions(self, request):
        service = self._get_service()
        transactions = service.get_transaction_history(request.user.id)
        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)