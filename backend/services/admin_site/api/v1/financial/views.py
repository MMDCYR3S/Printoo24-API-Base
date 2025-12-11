from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter

from core.models import OrderCostReport, OrderCostCatalog
from apps.financial.services import FinancialAppService
from .serializers import (
    CostReportListSerializer, CostReportDetailSerializer, 
    CreateCostReportInputSerializer, UpdateCostReportInputSerializer,
    CostItemInputSerializer, CostItemOutputSerializer,
    CostCatalogSerializer, ApprovalInputSerializer
)

# ========== Financial Catalog ViewSet ========== #
@extend_schema(tags=['Financial - Master Data'])
class FinancialCatalogViewSet(viewsets.ModelViewSet):
    """ مدیریت داده‌های پایه هزینه‌ها (CRUD ساده) """
    permission_classes = [IsAuthenticated]
    queryset = OrderCostCatalog.objects.select_related('cost_type').all()
    serializer_class = CostCatalogSerializer

# ========== Financial Report ViewSet ========== #
@extend_schema(tags=['Financial - Cost Reports'])
class FinancialReportViewSet(viewsets.GenericViewSet):
    """
    کنترلر اصلی مدیریت گزارشات مالی.
    تمام عملیات منطقی به FinancialAppService واگذار می‌شود.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FinancialAppService()

    def get_queryset(self):
        return OrderCostReport.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CostReportListSerializer
        elif self.action == 'retrieve':
            return CostReportDetailSerializer
        elif self.action == 'create':
            return CreateCostReportInputSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UpdateCostReportInputSerializer
        return CostReportDetailSerializer

    # ===== LIST & RETRIEVE (Read) =====
    def list(self, request):
        queryset = self.service._report_repo.model.objects.select_related('order', 'created_by').all().order_by('-created_at')
        page = self.paginate_queryset(queryset)
        serializer = CostReportListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        report = self.service.get_report_details(request.user, pk)
        serializer = CostReportDetailSerializer(report)
        return Response(serializer.data)

    # ===== CREATE (Write) =====
    def create(self, request):
        serializer = CreateCostReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        report = self.service.create_manual_cost(
            user=request.user,
            order_id=data['order_id'],
            data=data
        )
        
        return Response(CostReportDetailSerializer(report).data, status=status.HTTP_201_CREATED)

    # ===== UPDATE (Write) =====
    def partial_update(self, request, pk=None):
        serializer = UpdateCostReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        report = self.service.update_cost_report(
            user=request.user,
            report_id=pk,
            data=serializer.validated_data
        )
        return Response(CostReportDetailSerializer(report).data)

    # ===== DESTROY (Write) =====
    def destroy(self, request, pk=None):
        self.service.delete_cost_report(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== CUSTOM ACTIONS =====
    
    @extend_schema(request=ApprovalInputSerializer, responses=CostReportDetailSerializer)
    @action(detail=True, methods=['post'], url_path='approve')
    def approve_report(self, request, pk=None):
        """ تایید یا لغو تایید مالی """
        serializer = ApprovalInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        report = self.service.toggle_approval(
            user=request.user,
            report_id=pk,
            approve=serializer.validated_data['approve']
        )
        return Response(CostReportDetailSerializer(report).data)

    @extend_schema(request=CostItemInputSerializer, responses=CostItemOutputSerializer)
    @action(detail=True, methods=['post'], url_path='add-item')
    def add_item(self, request, pk=None):
        """ افزودن یک قلم هزینه به گزارش موجود """
        serializer = CostItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        item = self.service.add_item_to_report(
            user=request.user,
            report_id=pk,
            data=serializer.validated_data
        )
        return Response(CostItemOutputSerializer(item).data, status=status.HTTP_201_CREATED)

# ========== Financial Item ViewSet ========== #
@extend_schema(tags=['Financial - Cost Items'])
class FinancialItemViewSet(viewsets.GenericViewSet):
    """
    مدیریت ریز اقلام (فقط ویرایش و حذف).
    ایجاد از طریق Report انجام می‌شود.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FinancialAppService()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CostItemInputSerializer
        return CostItemOutputSerializer

    def partial_update(self, request, pk=None):
        serializer = CostItemInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        item = self.service.update_item(
            user=request.user,
            item_id=pk,
            data=serializer.validated_data
        )
        return Response(CostItemOutputSerializer(item).data)

    def destroy(self, request, pk=None):
        self.service.delete_item(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
