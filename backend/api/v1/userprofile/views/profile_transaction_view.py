from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample

from core.financial.services import QuotationService, PaymentService
from apps.userprofile.services import WalletAppService
from ..serializers import (
    WalletSerializer, WalletTransactionSerializer,
    QuotationCustomerSerializer,
    QuotationApprovalSerializer,
    WalletPaymentSerializer,
    PaymentCustomerSerializer
)

# ===== Wallet Detail API View ===== #
@extend_schema(tags=["Profile"])
class WalletDetailAPIView(APIView):
    """نمایش موجودی کیف پول کاربر"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="مشاهده موجودی کیف پول",
        responses={200: WalletSerializer},
        examples=[
            OpenApiExample(
                'Balance Example',
                value={
                    "decimal": "5000000.00",
                    "updated_at": "2023-11-20T10:30:00Z"
                }
            )
        ]
    )
    def get(self, request):
        self.service = WalletAppService(user=request.user)
        wallet = self.service.get_wallet_balance(request.user.id)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

# ===== Wallet History APIView ===== #
@extend_schema(tags=["Profile"])
class WalletHistoryAPIView(APIView):
    """نمایش لیست تراکنش‌های کاربر"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="تاریخچه تراکنش‌های کیف پول",
        description="لیست واریزها، برداشت‌ها و پرداخت‌های سفارش.",
        responses={200: WalletTransactionSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Transaction History',
                summary='لیست تراکنش‌ها',
                description='شامل یک شارژ حساب و یک پرداخت سفارش',
                value=[
                    {
                        "id": 101,
                        "type": "1",
                        "type_display": "افزایش",
                        "amount": "1000000.00",
                        "amount_after": "1000000.00",
                        "created_at": "2023-11-01T08:00:00Z"
                    },
                    {
                        "id": 105,
                        "type": "6",
                        "type_display": "پرداخت",
                        "amount": "-250000.00",
                        "amount_after": "750000.00",
                        "created_at": "2023-11-05T09:30:00Z"
                    }
                ]
            )
        ]
    )
    def get(self, request):
        self.service = WalletAppService(user=request.user)
        transactions = self.service.get_transaction_history(request.user.id)
        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

@extend_schema(tags=["Financial"])
class QuotationApprovalAPIView(APIView):
    """
    تأیید پیش‌فاکتور توسط مشتری
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="تأیید پیش‌فاکتور",
        request=QuotationApprovalSerializer,
        responses={200: QuotationCustomerSerializer},
    )
    def post(self, request, quotation_id):
        service = QuotationService()
        quotation = service.approve_quotation(quotation_id, user=request.user)
        serializer = QuotationCustomerSerializer(quotation)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Financial"])
class WalletPaymentAPIView(APIView):
    """
    پرداخت سفارش با کیف پول
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="پرداخت سفارش از کیف پول",
        request=WalletPaymentSerializer,
        responses={200: PaymentCustomerSerializer},
    )
    def post(self, request):
        serializer = WalletPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_id = serializer.validated_data['order_id']
        amount = serializer.validated_data.get('amount')

        service = PaymentService()
        payment = service.pay_with_wallet(order_id, request.user, amount)
        return Response(
            PaymentCustomerSerializer(payment).data,
            status=status.HTTP_200_OK,
        )
