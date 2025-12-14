from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.financial.services import FinancialQuotationAppService
from ..serializers import (
    QuotationDetailSerializer, CreateQuotationInputSerializer, ConvertQuotationInputSerializer
)

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
        
        data = serializer.validated_data
        items = data.pop('items')
        
        quo = self.service.create_quotation(request.user, data, items)
        return Response(QuotationDetailSerializer(quo).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=ConvertQuotationInputSerializer)
    @action(detail=True, methods=['post'], url_path='convert')
    def convert(self, request, pk=None):
        """ تبدیل استعلام به سفارش """
        serializer = ConvertQuotationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order = self.service.convert_to_order(
            request.user, 
            quotation_id=pk, 
            address_id=serializer.validated_data['address_id']
        )
        return Response({"order_id": order.id, "message": "تبدیل با موفقیت انجام شد."}, status=status.HTTP_200_OK)