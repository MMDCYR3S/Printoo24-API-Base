from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError

from core.models import OrderCostReport, OrderCostCatalog
from apps.financial.services import FinancialAppService
from .serializers import (
    CostReportListSerializer, CostReportDetailSerializer, 
    CreateCostReportInputSerializer, UpdateCostReportInputSerializer,
    CostItemInputSerializer, CostItemOutputSerializer,
    CostCatalogSerializer, ApprovalInputSerializer,
    InvoiceDetailSerializer, TransactionInputSerializer, 
    TransactionDetailSerializer, TransactionVerifySerializer,
    TransactionUpdateInputSerializer, InvoiceUpdateInputSerializer,
    CreateInvoiceInputSerializer,
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
        serializer = CostReportListSerializer(queryset, many=True)
        return Response(serializer.data)

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
        
        # ===== اعتبارسنجی اینکه آیا از قبل تایید شده یا خیر. اگر بله، خطا دهد ===== #
        report = self.service.get_report_details(request.user, pk)
        if report.is_approved_by_finance:
            raise ValidationError("گزارش تایید شده است و امکان تغییر وضیعت آن وجود ندارد.")
        
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

# ========== Financial Invoice ViewSet ========== #
@extend_schema(tags=['Financial - Invoices'])
class FinancialInvoiceViewSet(viewsets.GenericViewSet):
    """ مدیریت فاکتورها و تراکنش‌ها """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FinancialAppService()

    def retrieve(self, request, pk=None):
        """ دریافت جزئیات فاکتور """
        invoice = self.service.get_invoice_details(request.user, pk)
        if not invoice:
            return Response({"detail": "فاکتور یافت نشد"}, status=404)
        return Response(InvoiceDetailSerializer(invoice).data)
    
    @action(detail=True, methods=['post'], url_path='recalculate')
    def recalculate(self, request, pk=None):
        """ به‌روزرسانی مبالغ فاکتور (در صورت تغییر هزینه‌های سفارش) """
        invoice = self.service.recalculate_invoice_manually(request.user, pk)
        return Response(InvoiceDetailSerializer(invoice).data)
    
    @extend_schema(request=TransactionInputSerializer, responses=TransactionDetailSerializer)
    @action(detail=True, methods=['post'], url_path='add-transaction')
    def add_transaction(self, request, pk=None):
        """ ثبت تراکنش دستی روی این فاکتور """
        serializer = TransactionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        trx = self.service.register_payment(
            user=request.user, 
            invoice_id=pk, 
            data=serializer.validated_data
        )
        return Response(TransactionDetailSerializer(trx).data, status=status.HTTP_201_CREATED)
    
    @extend_schema(request=InvoiceUpdateInputSerializer, responses=InvoiceDetailSerializer)
    def partial_update(self, request, pk=None):
        """ ویرایش توضیحات یا سررسید فاکتور """
        serializer = InvoiceUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invoice = self.service.update_invoice(
            request.user, 
            invoice_id=pk, 
            data=serializer.validated_data
        )
        return Response(InvoiceDetailSerializer(invoice).data)

    def destroy(self, request, pk=None):
        """ حذف فاکتور (در صورت نداشتن تراکنش معتبر) """
        self.service.delete_invoice(request.user, invoice_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='finalize')
    def finalize(self, request, pk=None):
        """ تبدیل به فاکتور رسمی """
        invoice = self.service.finalize_invoice(request.user, pk)
        return Response(InvoiceDetailSerializer(invoice).data)
    
    @extend_schema(request=CreateInvoiceInputSerializer, responses=InvoiceDetailSerializer)
    def create(self, request):
        """ 
        صدور دستی فاکتور برای یک سفارش.
        (فقط در صورتی که سفارش فاقد فاکتور باشد استفاده می‌شود)
        """
        serializer = CreateInvoiceInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invoice = self.service.create_invoice_manually(
            user=request.user, 
            order_id=serializer.validated_data['order_id']
        )
        return Response(InvoiceDetailSerializer(invoice).data, status=status.HTTP_201_CREATED)
    
# ========== Financial Catalog ViewSet ========== #
@extend_schema(tags=['Financial - Transactions'])
class FinancialTransactionViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FinancialAppService()
    
    @extend_schema(request=TransactionVerifySerializer)
    @action(detail=True, methods=['post'], url_path='verify')
    def verify(self, request, pk=None):
        """ تایید یا رد تراکنش """
        serializer = TransactionVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        trx = self.service.verify_payment(
            user=request.user, 
            transaction_id=pk, 
            approved=serializer.validated_data['approved'],
            reason=serializer.validated_data.get('rejection_reason')
        )
        return Response(TransactionDetailSerializer(trx).data)
    
    @extend_schema(request=TransactionUpdateInputSerializer, responses=TransactionDetailSerializer)
    def partial_update(self, request, pk=None):
        """ ویرایش تراکنش (اگر تایید نشده باشد) """
        serializer = TransactionUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        trx = self.service.update_transaction(
            request.user, 
            transaction_id=pk, 
            data=serializer.validated_data
        )
        return Response(TransactionDetailSerializer(trx).data)

    def destroy(self, request, pk=None):
        """ حذف تراکنش (اگر تایید نشده باشد) """
        self.service.delete_transaction(request.user, transaction_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    