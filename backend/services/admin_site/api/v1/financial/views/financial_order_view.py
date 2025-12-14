from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.financial.services import FinancialOrderAppService
from ..serializers import (
    CostCatalogSerializer, OrderCostSheetSerializer,
    OrderCostReportListSerializer, OrderCostReportDetailSerializer,
    ApproveReportInputSerializer
)
from core.models import OrderCostCategory

# ===== 1. Master Data ViewSet ===== #
@extend_schema(tags=['Financial - Master Data'])
class FinancialCatalogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = OrderCostCategory.objects.all()
    serializer_class = CostCatalogSerializer

# ===== 2. Order Costing ViewSet ===== #
@extend_schema(tags=['Financial - Order Costing'])
class FinancialOrderCostViewSet(viewsets.GenericViewSet):
    """ 
    مدیریت بهای تمام شده (Cost Accounting).
    شامل تایید گزارشات و مشاهده شیت.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FinancialOrderAppService()

    @action(detail=True, methods=['get'], url_path='sheet')
    def get_sheet(self, request, pk=None):
        """ pk: Order ID - دریافت شیت مالی سفارش """
        sheet = self.service.get_order_cost_sheet(request.user, order_id=pk)
        return Response(OrderCostSheetSerializer(sheet).data)

    @action(detail=True, methods=['post'], url_path='lock')
    def lock_sheet(self, request, pk=None):
        """ pk: Order ID - قفل کردن حساب سفارش """
        self.service.lock_order_costs(request.user, order_id=pk)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='reports')
    def list_reports(self, request, pk=None):
        """ pk: Order ID - لیست تمام گزارشات هزینه این سفارش """
        reports = self.service.get_order_reports(request.user, order_id=pk)
        return Response(OrderCostReportListSerializer(reports, many=True).data)

# ===== 3. Report Approval ViewSet (On Report ID) ===== #
@extend_schema(tags=['Financial - Report Approval'])
class FinancialReportActionViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FinancialOrderAppService()

    def retrieve(self, request, pk=None):
        """ pk: Report ID - مشاهده جزئیات گزارش جهت تایید """
        report = self.service.get_report_detail(request.user, report_id=pk)
        return Response(OrderCostReportDetailSerializer(report).data)

    @extend_schema(request=ApproveReportInputSerializer)
    @action(detail=True, methods=['post'], url_path='decide')
    def decide(self, request, pk=None):
        """ pk: Report ID - تایید یا رد گزارش """
        serializer = ApproveReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if serializer.validated_data['approve']:
            self.service.approve_report(request.user, report_id=pk)
        else:
            self.service.reject_report(
                request.user,
                report_id=pk
            )
        return Response(status=status.HTTP_200_OK)