from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.financial.services import FinancialTransactionAppService
from ..serializers import (
    TransactionDetailSerializer, TransactionInputSerializer, TransactionVerifySerializer
)

@extend_schema(tags=['Financial - Transactions'])
class FinancialTransactionViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FinancialTransactionAppService()
    
    @extend_schema(request=TransactionInputSerializer)
    def create(self, request):
        """ ثبت تراکنش جدید (دستی) """
        serializer = TransactionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        invoice_id = data.pop('invoice_id')
        
        trx = self.service.register_manual_payment(request.user, invoice_id, data)
        return Response(TransactionDetailSerializer(trx).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=TransactionVerifySerializer)
    @action(detail=True, methods=['post'], url_path='verify')
    def verify(self, request, pk=None):
        """ تایید یا رد تراکنش """
        serializer = TransactionVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        trx = self.service.verify_transaction(
            request.user, 
            transaction_id=pk, 
            approved=serializer.validated_data['approved'],
            reason=serializer.validated_data.get('rejection_reason')
        )
        return Response(TransactionDetailSerializer(trx).data)
    
    @extend_schema(request=TransactionInputSerializer)
    def partial_update(self, request, pk=None):
        """ ویرایش تراکنش (معلق) """
        serializer = TransactionInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        trx = self.service.update_transaction(
            request.user, 
            transaction_id=pk, 
            data=serializer.validated_data
        )
        return Response(TransactionDetailSerializer(trx).data)

    def destroy(self, request, pk=None):
        """ حذف تراکنش (معلق) """
        self.service.delete_transaction(request.user, transaction_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
