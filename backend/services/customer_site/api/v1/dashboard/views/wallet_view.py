from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.dashboard.services import WalletDashboardService
from ..serializers.general_serializers import (
    WalletDetailSerializer, 
    WalletAdjustmentSerializer, 
    WalletTransactionSerializer
)

# ===== ویو‌ست مدیریت کیف پول ===== #
@extend_schema(tags=["Dashboard-Wallet"])
class WalletViewSet(viewsets.GenericViewSet, 
                    mixins.ListModelMixin, 
                    mixins.RetrieveModelMixin):
    """
    مدیریت کیف پول کاربران.
    ادمین می‌تواند لیست را ببیند و موجودی را به صورت دستی کم یا زیاد کند.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = WalletDashboardService()

    def get_queryset(self):
        return self.service.get_wallets_queryset()

    def get_serializer_class(self):
        if self.action == 'adjust_balance':
            return WalletAdjustmentSerializer
        return WalletDetailSerializer

    # ===== اکشن: تغییر موجودی (RPC Style) ===== #
    @extend_schema(
        summary="تغییر موجودی دستی",
        description="افزایش یا کاهش موجودی کیف پول کاربر توسط ادمین",
        request=WalletAdjustmentSerializer,
        responses={200: WalletDetailSerializer}
    )
    @action(detail=True, methods=['post'], url_path='adjust')
    def adjust_balance(self, request, pk=None):
        wallet = self.get_object()
        
        serializer = WalletAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            # ===== عملیات بروزرسانی کیف پول ===== #
            updated_wallet = self.service.adjust_balance(
                user_id=wallet.user_id,
                amount=data['amount'],
                action_type=data['action_type']
            )
            
            output_serializer = WalletDetailSerializer(updated_wallet)
            return Response(output_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== اکشن: مشاهده تراکنش‌های کاربر ===== #
    @extend_schema(summary="تاریخچه تراکنش‌ها")
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        wallet = self.get_object()
        transactions = wallet.user.wallet_transactions.all().order_by('-created_at')
        
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = WalletTransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)