from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.dashboard.services import WalletDashboardService
from ..serializers import (
    WalletListSerializer, 
    WalletAdjustmentSerializer,
    WalletTransactionSerializer
)
from apps.accounts.models import Wallet

# ===== Wallet View Set ===== #
@extend_schema(tags=['Dashboard-Wallet'])
class WalletViewSet(viewsets.ViewSet):
    """
    مدیریت کیف پول کاربران توسط ادمین.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = WalletDashboardService()

    # ===== لیست کیف پول‌ها ===== #
    @extend_schema(responses=WalletListSerializer(many=True))
    def list(self, request):
        queryset = self.service.get_wallets_queryset()
        serializer = WalletListSerializer(queryset, many=True)
        return Response(serializer.data)

    # ===== تغییر موجودی ===== #
    @extend_schema(
        summary="تغییر موجودی دستی (واریز/برداشت)",
        request=WalletAdjustmentSerializer,
        responses=WalletListSerializer,
        description=
        """
        این بخش نیازمند ID مربوط به کیف پول کاربر می باشد. برای اضافه کردن
        یا کسر یک موجودی، باید نوع اون رو مشخص کرد. انواعی که تا به الان
        ایجاد شده عبارتند از:\n
        کسر وجه - deposit\n
        افزایش وجه - debit\n
        بخش مربوط به action_type باید یکی از این دو مقدار رو بگیره.
        حالا بسته به این در amount چه تعدادی بزاری و البته کدوم نوع رو
        انتخاب کنی، این قسمت موجودی رو کم و زیاد میکنه.
        """
    )
    @action(detail=True, methods=['post'], url_path='adjust')
    def adjust_balance(self, request, pk=None):
        """ 
        بخش ایجاد یا ویرایش تراکشن
        """
        try:
            wallet = Wallet.objects.get(pk=pk)
            user_id = wallet.user_id
        except Wallet.DoesNotExist:
             return Response({'detail': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = WalletAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updated_wallet = self.service.adjust_balance(
            user_id=user_id,
            amount=serializer.validated_data['amount'],
            action_type=serializer.validated_data['action_type'],
        )
        
        return Response(WalletListSerializer(updated_wallet).data, status=status.HTTP_200_OK)

    # ===== تاریخچه تراکنش‌ها ===== #
    @extend_schema(summary="تاریخچه تراکنش‌های یک کیف پول")
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        try:
            wallet = Wallet.objects.get(pk=pk)
            # استفاده از related_name مدل WalletTransaction (باید در مدل تعریف شده باشد)
            # فرض: user.wallet_transactions
            transactions = wallet.user.wallet_transactions.all().order_by('-created_at')
            
            serializer = WalletTransactionSerializer(transactions, many=True)
            return Response(serializer.data)
        except Wallet.DoesNotExist:
            return Response({'detail': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
