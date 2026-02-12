from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.accounts.exceptions import InsufficientFundsException
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
        summary="تغییر موجودی با شناسه کاربر (واریز/برداشت)",
        description="در این متد نیازی به دانستن ID کیف پول نیست، فقط ID کاربر را ارسال کنید.",
        request=WalletAdjustmentSerializer,
        responses={200: WalletListSerializer},
        examples=[
            OpenApiExample(
                'مثال واریز (افزایش)',
                value={'user_id': 10, 'amount': '100000.00', 'action_type': 'deposit'},
                request_only=True,
            ),
        ]
    )
    @action(detail=False, methods=['post'], url_path='adjust-balance')
    def adjust_balance(self, request):
        
        # ===== اعتبارسنجی ورودی ===== #
        serializer = WalletAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        amount = serializer.validated_data['amount']
        action_type = serializer.validated_data['action_type']

        # ===== اجرای عملیات اصلاح موجودی ===== #
        try:
            updated_wallet = self.service.adjust_balance(
                user_id=user_id,
                amount=amount,
                action_type=action_type,
            )
            
            # ===== بازگشت اطلاعات کیف پول به‌روزرسانی شده ===== #
            return Response(WalletListSerializer(updated_wallet).data, status=status.HTTP_200_OK)
            
        except NotFound as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except (InsufficientFundsException, ValidationError) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': 'خطای سیستمی رخ داده است.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ===== تاریخچه تراکنش‌ها ===== #
    @extend_schema(summary="تاریخچه تراکنش‌های یک کیف پول")
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        try:
            wallet = Wallet.objects.get(pk=pk)
            transactions = wallet.user.wallet_transactions.all().order_by('-created_at')
            
            serializer = WalletTransactionSerializer(transactions, many=True)
            return Response(serializer.data)
        except Wallet.DoesNotExist:
            return Response({'detail': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
