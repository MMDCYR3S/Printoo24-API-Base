from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.financial.services import FinancialQuotationAppService
from ..serializers import (
    QuotationDetailSerializer, CreateQuotationInputSerializer,
    ConvertQuotationInputSerializer, UpdateQuotationInputSerializer, InvoiceDetailSerializer
)

# ========== Financial Quotation ViewSet ========== #
@extend_schema(tags=['Financial - Quotations'])
class FinancialQuotationViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FinancialQuotationAppService()

    def retrieve(self, request, pk=None):
        quo = self.service.get_quotation_detail(request.user, pk)
        return Response(QuotationDetailSerializer(quo).data)

    @extend_schema(request=CreateQuotationInputSerializer)
    def create(self, request):
        serializer = CreateQuotationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quo = self.service.create_quotation(request.user, serializer.validated_data)
        return Response(QuotationDetailSerializer(quo).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=UpdateQuotationInputSerializer)
    def partial_update(self, request, pk=None):
        """ ویرایش اطلاعات پیش‌فاکتور """
        serializer = UpdateQuotationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quo = self.service.update_quotation(request.user, pk, serializer.validated_data)
        return Response(QuotationDetailSerializer(quo).data)

    def destroy(self, request, pk=None):
        """ حذف پیش‌فاکتور """
        self.service.delete_quotation(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='convert')
    def convert(self, request, pk=None):
        """ 
        این متد پیش‌فاکتور را گرفته و برای سفارش مشخص شده، فاکتور صادر می‌کند.
        """
        serializer = ConvertQuotationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # تبدیل انجام می‌شود و فاکتور برمی‌گردد
        invoice = self.service.convert_to_invoice(
            request.user, 
            quotation_id=pk, 
            order_id=serializer.validated_data['order_id']
        )
        
        return Response(
            InvoiceDetailSerializer(invoice).data, 
            status=status.HTTP_201_CREATED
        )