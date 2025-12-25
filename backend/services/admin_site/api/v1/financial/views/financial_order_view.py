from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.financial.services import FinancialOrderAppService
from apps.order.models import OrderCostCategory, OrderCostSheet, OrderCostReport

# Import Serializers (Assuming they are in serializers.py)
from ..serializers import (
    OrderCostReportDetailSerializer, ApproveReportInputSerializer,
    CreateReportInputSerializer, UpdateReportInputSerializer, 
    CostItemInputSerializer, OrderCostItemSerializer,
    OrderCostReportListSerializer, CostCatalogSerializer, CostCatalogInputSerializer,
    OrderCostSheetSerializer, UpdateSheetInputSerializer,
    CreateSheetInputSerializer
)

class BaseFinancialViewSet(viewsets.GenericViewSet):
    """ کلاس پایه برای تزریق سرویس """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FinancialOrderAppService()


# ===== 1. Master Data ViewSet (Categories) ===== #
@extend_schema(tags=['Financial - Cost Category'])
class FinancialCatalogViewSet(BaseFinancialViewSet):
    permission_classes = [IsAuthenticated]
    
    queryset = OrderCostCategory.objects.all() 
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CostCatalogInputSerializer
        return CostCatalogSerializer

    def list(self, request):
        """ دریافت یک مورد (کاتالوگ) با ID """
        category = self.service.get_all_categories(request.user)
        return Response(CostCatalogSerializer(category, many=True).data)
    
    def retrieve(self, request, pk=None):
        """ دریافت یک مORDER_COST_CATEGORY با ID """
        category = self.service._category_repo.get_by_id(pk)
        return Response(CostCatalogSerializer(category).data)

    def create(self, request):
        serializer = CostCatalogInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = self.service.create_category(request.user, serializer.validated_data)
        return Response(CostCatalogSerializer(category).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        serializer = CostCatalogInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = self.service.update_category(request.user, pk, serializer.validated_data)
        return Response(CostCatalogSerializer(category).data)

    def destroy(self, request, pk=None):
        self.service.delete_category(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===== 2. Financial - Sheet Costing ViewSet ===== #
@extend_schema(tags=['Financial - Sheet Costing'])
class FinancialOrderCostViewSet(BaseFinancialViewSet):
    """ 
    مدیریت بهای تمام شده سفارشات (Ledger).
    """
    permission_classes = [IsAuthenticated]
    queryset = OrderCostSheet.objects.all() 
    serializer_class = OrderCostSheetSerializer

    @extend_schema(request=CreateSheetInputSerializer)
    def create(self, request):
        """ ایجاد دستی سند برای یک سفارش """
        serializer = CreateSheetInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        sheet = self.service.create_sheet(request.user, serializer.validated_data['order_id'])
        return Response(OrderCostSheetSerializer(sheet).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """ دریافت شیت با ID شیت """
        sheet = self.get_object() 
        return Response(OrderCostSheetSerializer(sheet).data)

    @extend_schema(request=UpdateSheetInputSerializer)
    def partial_update(self, request, pk=None):
        """ ویرایش سند (مثلاً تغییر وضعیت قفل) """
        serializer = UpdateSheetInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        sheet = self.service.update_sheet(request.user, pk, serializer.validated_data)
        return Response(OrderCostSheetSerializer(sheet).data)

    def destroy(self, request, pk=None):
        """ حذف سند """
        self.service.delete_sheet(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # ========== CUSTOM ACTIONS =========== #
    @action(detail=False, methods=['get'], url_path='by-order/(?P<order_id>\d+)')
    def get_by_order(self, request, order_id=None):
        """ دریافت شیت بر اساس شناسه سفارش """
        sheet = self.service.get_order_cost_sheet(request.user, order_id=int(order_id))
        return Response(OrderCostSheetSerializer(sheet).data)

    @action(detail=True, methods=['post'], url_path='lock')
    def lock_sheet(self, request, pk=None):
        """ قفل کردن حساب سفارش (pk در اینجا order_id نیست، بلکه sheet_id است، مگر اینکه در url تغییر دهید) """
        sheet = self.get_object()
        self.service.lock_order_costs(request.user, order_id=sheet.order_id)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='reports')
    def list_reports(self, request, pk=None):
        """ لیست تمام گزارشات هزینه این شیت """
        sheet = self.get_object()
        reports = self.service.get_order_reports(request.user, order_id=sheet.order_id)
        return Response(OrderCostReportListSerializer(reports, many=True).data)


# ===== 3. Report Management ViewSet ===== #
@extend_schema(tags=['Financial - Report Management'])
class FinancialReportActionViewSet(BaseFinancialViewSet):
    """
    مدیریت ریز گزارش‌ها و اقلام آن‌ها.
    """
    permission_classes = [IsAuthenticated]
    queryset = OrderCostReport.objects.all()
    
    @extend_schema(request=CreateReportInputSerializer, responses=OrderCostReportDetailSerializer)
    def create(self, request):
        """ ایجاد گزارش جدید + آیتم‌ها """
        serializer = CreateReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        items = data.pop('items')
        order_id = data.pop('order_id')
        
        report = self.service.create_report_manually(
            request.user, 
            order_id=order_id,
            data=data,
            items=items
        )
        return Response(OrderCostReportDetailSerializer(report).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """ مشاهده جزئیات گزارش """
        report = self.service.get_report_detail(request.user, report_id=pk)
        return Response(OrderCostReportDetailSerializer(report).data)

    @extend_schema(request=UpdateReportInputSerializer)
    def partial_update(self, request, pk=None):
        """ ویرایش هدر گزارش """
        serializer = UpdateReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        report = self.service.update_report(request.user, pk, serializer.validated_data)
        return Response(OrderCostReportDetailSerializer(report).data)

    def destroy(self, request, pk=None):
        self.service.delete_report(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ========== CUSTOM ACTIONS =========== #
    @extend_schema(request=ApproveReportInputSerializer)
    @action(detail=True, methods=['post'], url_path='decide')
    def decide(self, request, pk=None):
        """ تایید یا رد گزارش """
        serializer = ApproveReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if serializer.validated_data['approve']:
            self.service.approve_report(request.user, pk)
        else:
            self.service.reject_report(
                request.user, pk
            )
        return Response(status=status.HTTP_200_OK)

    # ========== CUSTOM ACTIONS =========== #
    @extend_schema(request=CostItemInputSerializer, responses=OrderCostItemSerializer)
    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
        """ افزودن قلم به این گزارش (pk = report_id) """
        serializer = CostItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        item = self.service.add_item_to_report(request.user, pk, serializer.validated_data)
        return Response(OrderCostItemSerializer(item).data, status=status.HTTP_201_CREATED)
    
    @extend_schema(request=CostItemInputSerializer, responses=OrderCostItemSerializer)
    @action(detail=True, methods=['patch'], url_path='items/(?P<item_id>\d+)')
    def update_item(self, request, pk=None, item_id=None):
        """ ویرایش یک قلم خاص از گزارش """
        serializer = CostItemInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        item = self.service.update_report_item(request.user, item_id, serializer.validated_data)
        return Response(OrderCostItemSerializer(item).data)

    @action(detail=True, methods=['delete'], url_path='items/(?P<item_id>\d+)')
    def delete_item(self, request, pk=None, item_id=None):
        """ حذف یک قلم خاص """
        self.service.delete_report_item(request.user, item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
