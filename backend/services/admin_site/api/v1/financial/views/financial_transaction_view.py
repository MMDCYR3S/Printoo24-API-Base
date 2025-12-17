from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema

from apps.financial.services import FinancialTransactionAppService
from ..serializers import (
    TransactionDetailSerializer, TransactionCreateInputSerializer, 
    TransactionUpdateSerializer, TransactionVerifySerializer
)

@extend_schema(tags=['Financial - Transactions'])
class FinancialTransactionViewSet(viewsets.GenericViewSet):
    """ مدیریت کامل تراکنش‌های مالی """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser] # برای آپلود عکس فیش
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FinancialTransactionAppService()
    
    # ===== List & Retrieve ===== #
    def list(self, request):
        """ مشاهده لیست تمام تراکنش‌ها """
        transactions = self.service.list_transactions(request.user, request.query_params)
        # صفحه‌بندی (Pagination) را می‌توان اینجا اضافه کرد
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = TransactionDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = TransactionDetailSerializer(transactions, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """ مشاهده جزئیات یک تراکنش """
        trx = self.service.get_transaction_detail(request.user, pk)
        return Response(TransactionDetailSerializer(trx).data)

    # ===== Create ===== #
    @extend_schema(request=TransactionCreateInputSerializer)
    def create(self, request):
        """ ثبت تراکنش جدید (دستی) """
        serializer = TransactionCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        invoice_id = data.pop('invoice_id')
        
        trx = self.service.register_manual_payment(request.user, invoice_id, data)
        return Response(TransactionDetailSerializer(trx).data, status=status.HTTP_201_CREATED)

    # ===== Update (PUT & PATCH) ===== #
    @extend_schema(request=TransactionUpdateSerializer)
    def update(self, request, pk=None):
        """ ویرایش کامل تراکنش (PUT) """
        serializer = TransactionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        trx = self.service.update_transaction(
            request.user, 
            transaction_id=pk, 
            data=serializer.validated_data
        )
        return Response(TransactionDetailSerializer(trx).data)

    @extend_schema(request=TransactionUpdateSerializer)
    def partial_update(self, request, pk=None):
        """ ویرایش جزئی تراکنش (PATCH) """
        serializer = TransactionUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        trx = self.service.update_transaction(
            request.user, 
            transaction_id=pk, 
            data=serializer.validated_data
        )
        return Response(TransactionDetailSerializer(trx).data)

    # ===== Delete ===== #
    def destroy(self, request, pk=None):
        """ حذف تراکنش (معلق) """
        self.service.delete_transaction(request.user, transaction_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== Verify Action ===== #
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
