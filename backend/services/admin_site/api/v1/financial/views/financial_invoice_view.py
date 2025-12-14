from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.financial.services import FinancialInvoiceAppService
from ..serializers import (
    InvoiceDetailSerializer, InvoiceUpdateInputSerializer, CreateInvoiceInputSerializer
)

@extend_schema(tags=['Financial - Invoices'])
class FinancialInvoiceViewSet(viewsets.GenericViewSet):
    """ مدیریت فاکتورهای فروش """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FinancialInvoiceAppService()

    def retrieve(self, request, pk=None):
        invoice = self.service.get_invoice_detail(request.user, pk)
        return Response(InvoiceDetailSerializer(invoice).data)
    
    @extend_schema(request=CreateInvoiceInputSerializer)
    def create(self, request):
        """ صدور دستی فاکتور """
        serializer = CreateInvoiceInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invoice = self.service.create_invoice_manually(
            request.user, 
            order_id=serializer.validated_data['order_id']
        )
        return Response(InvoiceDetailSerializer(invoice).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='recalculate')
    def recalculate(self, request, pk=None):
        """ به‌روزرسانی مبالغ فاکتور """
        invoice = self.service.recalculate_invoice(request.user, pk)
        return Response(InvoiceDetailSerializer(invoice).data)
    
    @action(detail=True, methods=['post'], url_path='finalize')
    def finalize(self, request, pk=None):
        """ تبدیل فاکتور به فاکتور نهایی """
        invoice = self.service.finalize_invoice(request.user, pk)
        return Response(InvoiceDetailSerializer(invoice).data)
    
    @extend_schema(request=InvoiceUpdateInputSerializer)
    def partial_update(self, request, pk=None):
        """ ویرایش متادیتا """
        serializer = InvoiceUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invoice = self.service.update_invoice_metadata(
            request.user, 
            invoice_id=pk, 
            data=serializer.validated_data
        )
        return Response(InvoiceDetailSerializer(invoice).data)

    def destroy(self, request, pk=None):
        self.service.delete_invoice(request.user, invoice_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)