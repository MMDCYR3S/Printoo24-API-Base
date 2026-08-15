from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from drf_spectacular.utils import extend_schema, OpenApiExample

from ..serializers import WalletSerializer, WalletTransactionSerializer, WalletAdjustmentSerializer
from apps.dashboard.services import WalletDashboardService
from apps.accounts.exceptions import InsufficientFundsException, WalletNotFoundException

@extend_schema(tags=["Dashboard - Wallet"])
class WalletViewSet(viewsets.ViewSet):
    """
    مدیریت کیف پول در داشبورد ادمین
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = WalletDashboardService()

    @extend_schema(
        summary="مشاهده موجودی و آمار کیف پول یک کاربر (نیاز به user_id)",
        parameters=[
            {
                'name': 'user_id',
                'in': 'query',
                'description': 'شناسه کاربر مورد نظر',
                'required': True,
                'schema': {'type': 'integer'},
            }
        ],
        responses={200: WalletSerializer},
    )
    @action(detail=False, methods=['get'], url_path='balance')
    def balance(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            raise ValidationError("پارامتر user_id الزامی است.")
        try:
            wallet = self.service.get_wallet_by_user_id(int(user_id))
        except WalletNotFoundException:
            raise NotFound("کیف پول کاربر یافت نشد.")
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

    @extend_schema(
        summary="تاریخچه تراکنش‌های کیف پول یک کاربر (نیاز به user_id)",
        parameters=[
            {
                'name': 'user_id',
                'in': 'query',
                'description': 'شناسه کاربر مورد نظر',
                'required': True,
                'schema': {'type': 'integer'},
            }
        ],
        responses={200: WalletTransactionSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='transactions')
    def transactions(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            raise ValidationError("پارامتر user_id الزامی است.")
        try:
            transactions = self.service.get_transactions_by_user_id(int(user_id))
        except WalletNotFoundException:
            raise NotFound("کیف پول کاربر یافت نشد.")
        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="تغییر موجودی با شناسه کاربر (واریز/برداشت)",
        description="در این متد نیازی به دانستن ID کیف پول نیست، فقط ID کاربر را ارسال کنید.",
        request=WalletAdjustmentSerializer,
        responses={200: WalletSerializer},
        examples=[
            OpenApiExample(
                'مثال واریز (افزایش)',
                value={'user_id': 10, 'amount': '100000', 'action_type': 'deposit', 'description': 'واریز توسط ادمین'},
                request_only=True,
            ),
            OpenApiExample(
                'مثال برداشت (کاهش)',
                value={'user_id': 10, 'amount': '100000', 'action_type': 'debit', 'description': 'برداشت توسط ادمین'},
                request_only=True,
            ),
        ]
    )
    @action(detail=False, methods=['post'], url_path='adjust-balance')
    def adjust_balance(self, request):
        serializer = WalletAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        amount = serializer.validated_data['amount']
        action_type = serializer.validated_data['action_type']
        description = serializer.validated_data.get('description', '')

        try:
            updated_wallet = self.service.adjust_balance(
                user_id=user_id,
                amount=amount,
                action_type=action_type,
                actor=request.user,
                description=description,
            )
            return Response(WalletSerializer(updated_wallet).data, status=status.HTTP_200_OK)
            
        except NotFound as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except InsufficientFundsException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # لاگ خطا برای دیباگ
            return Response({'detail': 'خطای سیستمی رخ داده است.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
