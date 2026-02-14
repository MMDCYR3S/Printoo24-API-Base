from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.financial.services import FinancialOrderAppService
from apps.order.models import OrderFinancialCategory, OrderFinancialSheet, OrderFinancialReport

# Import Serializers (Assuming they are in serializers.py)
from ..serializers import (
    OrderFinancialReportDetailSerializer, ApproveReportInputSerializer,
    CreateReportInputSerializer, UpdateReportInputSerializer, 
    FinancialItemInputSerializer, OrderFinancialItemSerializer,
    OrderFinancialReportListSerializer, FinancialCatalogSerializer, FinancialCatalogInputSerializer,
    OrderFinancialSheetSerializer, UpdateSheetInputSerializer,
    CreateSheetInputSerializer, CreateRevenueReportInputSerializer,
    BulkActionSerializer, 
)

class BaseFinancialViewSet(viewsets.GenericViewSet):
    """ کلاس پایه برای تزریق سرویس """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FinancialOrderAppService()


# ===== 1. Master Data ViewSet (Categories) ===== #
@extend_schema(tags=['Financial - Financial Category'])
class FinancialCatalogViewSet(BaseFinancialViewSet):
    permission_classes = [IsAuthenticated]
    
    queryset = OrderFinancialCategory.objects.all() 
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FinancialCatalogInputSerializer
        return FinancialCatalogSerializer

    def list(self, request):
        """ دریافت یک مورد (کاتالوگ) با ID """
        category = self.service.get_all_categories(request.user)
        return Response(FinancialCatalogSerializer(category, many=True).data)
    
    def retrieve(self, request, pk=None):
        """ دریافت یک مORDER_COST_CATEGORY با ID """
        category = self.service._category_repo.get_by_id(pk)
        return Response(FinancialCatalogSerializer(category).data)

    def create(self, request):
        serializer = FinancialCatalogInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = self.service.create_category(request.user, serializer.validated_data)
        return Response(FinancialCatalogSerializer(category).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        serializer = FinancialCatalogInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = self.service.update_category(request.user, pk, serializer.validated_data)
        return Response(FinancialCatalogSerializer(category).data)

    def destroy(self, request, pk=None):
        self.service.delete_category(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===== 2. Financial - Sheet Financialing ViewSet ===== #
@extend_schema(tags=['Financial - Sheet Financialing'])
class FinancialOrderFinancialViewSet(BaseFinancialViewSet):
    """ 
    مدیریت بهای تمام شده سفارشات (Ledger).
    """
    permission_classes = [IsAuthenticated]
    queryset = OrderFinancialSheet.objects.all() 
    serializer_class = OrderFinancialSheetSerializer

    @extend_schema(
        request=CreateReportInputSerializer, 
        responses={201: OrderFinancialReportDetailSerializer},
        examples=[
            OpenApiExample(
                name='Financial Report Creation', # نام مثال در سواگر
                description='یک نمونه کامل برای ارسال گزارش هزینه شامل آیتم‌ها و فایل‌های پیوست',
                value={
                    "order_id": 10,
                    "title": "هزینه چاپ و کاغذ بخش افست",
                    "financial_tag": 5,
                    "description": "خرید اقلام لازم برای سفارش شماره ۴۵۱۲",
                    "items": [
                        {
                            "catalog_id": 12,
                            "custom_title": "کاغذ کوتد 150 گرم",
                            "amount": "5500000",
                            "description": "50 بسته"
                        },
                        {
                            "catalog_id": 18,
                            "custom_title": "زینک قرمز",
                            "amount": "850000",
                            "description": "۲ عدد شیت"
                        }
                    ],
                    "attachments": [
                        "File_1",
                        "File_2"
                    ]
                }
            )
        ]
    )
    def create(self, request):
        """ ایجاد دستی سند برای یک سفارش """
        serializer = CreateSheetInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        sheet = self.service.create_sheet(request.user, serializer.validated_data['order_id'])
        return Response(OrderFinancialSheetSerializer(sheet).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """ دریافت شیت با ID شیت """
        sheet = self.get_object() 
        return Response(OrderFinancialSheetSerializer(sheet).data)

    @extend_schema(request=UpdateSheetInputSerializer)
    def partial_update(self, request, pk=None):
        """ ویرایش سند (مثلاً تغییر وضعیت قفل) """
        serializer = UpdateSheetInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        sheet = self.service.update_sheet(request.user, pk, serializer.validated_data)
        return Response(OrderFinancialSheetSerializer(sheet).data)

    def destroy(self, request, pk=None):
        """ حذف سند """
        self.service.delete_sheet(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # ========== CUSTOM ACTIONS =========== #
    @action(detail=False, methods=['get'], url_path='by-order/(?P<order_id>\d+)')
    def get_by_order(self, request, order_id=None):
        """ دریافت شیت بر اساس شناسه سفارش """
        sheet = self.service.get_order_cost_sheet(request.user, order_id=int(order_id))
        return Response(OrderFinancialSheetSerializer(sheet).data)

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
        return Response(OrderFinancialReportListSerializer(reports, many=True).data)


# ===== REPORT MANAGEMENT VIEWSET ===== #
@extend_schema(tags=['Financial - Cost Management'])
class FinancialReportActionViewSet(BaseFinancialViewSet):
    """
    مدیریت ریز گزارش‌ها و اقلام آن‌ها.
    """
    permission_classes = [IsAuthenticated]
    queryset = OrderFinancialReport.objects.filter(nature='cost')

    # ========== LIST ========== #
    def list(self, request):
        """ مشاهده لیست گزارشات """
        reports = self.queryset.all()
        serializer = OrderFinancialReportListSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ========== CREATE ========== #
    # ===== CREATE REVENUE ===== #
    @extend_schema(
        request=CreateRevenueReportInputSerializer,
        responses={201: OrderFinancialReportDetailSerializer},
        examples=[
            OpenApiExample(
                name='Create Invoice Revenue',
                description='ثبت درآمد حاصل از پرداخت فاکتور توسط مشتری',
                value={
                    "order_id": 105,
                    "title": "درآمد فروش - پیش‌پرداخت",
                    "financial_tag_id": 2, # مثلاً تگ "فروش محصول"
                    "description": "واریز نقدی مشتری بابت ۵۰ درصد پیش‌پرداخت",
                    "items": [
                        {
                            "custom_title": "پیش‌پرداخت فاکتور #1025",
                            "amount": "15000000",
                            "description": "واریز به حساب ملت"
                        }
                    ],
                    "attachments": [] 
                }
            ),
            OpenApiExample(
                name='Create Extra Service Revenue',
                description='ثبت درآمد بابت خدمات اضافه (مثل طراحی اختصاصی یا ارسال ویژه)',
                value={
                    "order_id": 105,
                    "title": "هزینه خدمات جانبی",
                    "financial_tag_id": 4, # مثلاً تگ "خدمات جانبی"
                    "items": [
                        {
                            "catalog_id": 12, # مثلاً دسته‌بندی "طراحی لوگو"
                            "amount": "2000000",
                            "description": "طراحی لوگوی اختصاصی"
                        },
                        {
                            "custom_title": "تیپاکس ویژه",
                            "amount": "150000",
                            "description": "درخواست ارسال سریع"
                        }
                    ]
                }
            )
        ]
    )
    def create(self, request):
        """ ایجاد گزارش جدید + آیتم‌ها """
        serializer = CreateReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        items = data.pop('items', None)
        attachments = data.pop('attachments', None)
        order_id = data.pop('order_id')
        
        report = self.service.create_report_manually(
            request.user, 
            order_id=order_id,
            data=data,
            items=items,
            attachments=attachments
        )
        return Response(OrderFinancialReportDetailSerializer(report).data, status=status.HTTP_201_CREATED)

    # ========== RETRIEVE ========== #
    def retrieve(self, request, pk=None):
        """ مشاهده جزئیات گزارش """
        report = self.service.get_report_detail(request.user, report_id=pk)
        return Response(OrderFinancialReportDetailSerializer(report).data)

    # ========== UPDATE ========== #
    @extend_schema(request=UpdateReportInputSerializer)
    def partial_update(self, request, pk=None):
        """ ویرایش هدر گزارش """
        serializer = UpdateReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        report = self.service.update_report(request.user, pk, serializer.validated_data)
        return Response(OrderFinancialReportDetailSerializer(report).data)

    # ========== DELETE ========== #
    def destroy(self, request, pk=None):
        self.service.delete_report(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ========== APPROVE ACTION =========== #
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

    # ========== ADD ITEM ACTIONS =========== #
    @extend_schema(
        request=FinancialItemInputSerializer,
        responses=OrderFinancialItemSerializer,
        examples=[
            OpenApiExample(
                name='Add Revenue Item',
                description='افزودن یک قلم درآمدی جدید به گزارش موجود',
                value={
                    "custom_title": "مابه التفاوت کاغذ",
                    "amount": "500000",
                    "description": "افزایش قیمت کاغذ گلاسه"
                }
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
        """ افزودن قلم به این گزارش (pk = report_id) """
        serializer = FinancialItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        item = self.service.add_item_to_report(request.user, pk, serializer.validated_data)
        return Response(OrderFinancialItemSerializer(item).data, status=status.HTTP_201_CREATED)
    
    # ========== UPDATE ITEM ACTION ========== #
    @extend_schema(request=FinancialItemInputSerializer, responses=OrderFinancialItemSerializer)
    @action(detail=True, methods=['patch'], url_path='item/(?P<item_id>\d+)')
    def update_item(self, request, pk=None, item_id=None):
        """ ویرایش یک قلم خاص از گزارش """
        serializer = FinancialItemInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        item = self.service.update_report_item(request.user, item_id, serializer.validated_data)
        return Response(OrderFinancialItemSerializer(item).data)

    # ========== DELETE ITEM ACTION ========== #
    @action(detail=True, methods=['delete'], url_path='items/(?P<item_id>\d+)')
    def delete_item(self, request, pk=None, item_id=None):
        """ حذف یک قلم خاص """
        self.service.delete_report_item(request.user, item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

# ===== REVENUE MANAGEMENT VIEWSET ===== #
@extend_schema(tags=['Financial - Revenue Management'])
class RevenueReportViewSet(BaseFinancialViewSet):
    """
    مدیریت اختصاصی درآمدهای سفارش توسط واحد مالی.
    """
    permission_classes = [IsAuthenticated]
    queryset = OrderFinancialReport.objects.filter(nature='revenue')
    serializer_class = OrderFinancialReportDetailSerializer

    # ===== LIST & SEARCH REVENUES ===== #
    def list(self, request):
        revenues = self.queryset.all()
        return Response(OrderFinancialReportListSerializer(revenues, many=True).data)

    # ===== RETRIEVE REVENUE DETAIL ===== #
    def retrieve(self, request, pk=None):
        """ 
        مشاهده جزئیات کامل یک درآمد.
        چرایی: مالی باید بتواند ریز اقلام یک درآمد ثبت شده را ببیند.
        """
        report = self.service.get_report_detail(request.user, report_id=pk)
        
        if report.nature != 'revenue':
            return Response({"detail": "فایل مورد نظر درآمد نیست."}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(OrderFinancialReportDetailSerializer(report).data)

    # ===== CREATE REVENUE ===== #
    @extend_schema(
        request=CreateRevenueReportInputSerializer,
        responses={201: OrderFinancialReportDetailSerializer},
        examples=[
            OpenApiExample(
                name='Create Invoice Revenue',
                description='ثبت درآمد حاصل از پرداخت فاکتور',
                value={
                    "order_id": 105,
                    "title": "درآمد فروش - پیش‌پرداخت",
                    "financial_tag_id": 2, 
                    "description": "واریز نقدی مشتری بابت ۵۰ درصد پیش‌پرداخت",
                    "items": [
                        {
                            "custom_title": "پیش‌پرداخت فاکتور #1025",
                            "amount": "15000000",
                            "description": "واریز به حساب ملت"
                        }
                    ],
                    "attachments": [] 
                }
            )
        ]
    )
    def create(self, request):
        serializer = CreateRevenueReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        report = self.service.create_revenue_report(
            user=request.user,
            order_id=serializer.validated_data.pop('order_id'),
            data=serializer.validated_data,
            items=serializer.validated_data.pop('items', []),
            attachments=request.FILES.getlist('attachments')
        )
        return Response(OrderFinancialReportDetailSerializer(report).data, status=status.HTTP_201_CREATED)

    # ===== UPDATE REPORT HEADER ===== #
    @extend_schema(
        request=UpdateReportInputSerializer,
        responses=OrderFinancialReportDetailSerializer,
        examples=[
            OpenApiExample(
                name='Update Revenue Header',
                description='ویرایش اطلاعات کلی گزارش (بدون تغییر اقلام)',
                value={
                    "title": "درآمد اصلاح شده - فاکتور ۱۰۲",
                    "description": "توضیحات تکمیلی بابت واریز به حساب سامان (اصلاح شناسه واریز)",
                    "financial_tag_id": 3
                }
            )
        ]
    )
    def partial_update(self, request, pk=None):
        """ فقط ویرایش هدر گزارش درآمد """
        report = self.service.update_report(request.user, pk, request.data)
        return Response(OrderFinancialReportDetailSerializer(report).data)

    # ===== ITEM ACTIONS (SEPARATE EDIT) ===== #
    @extend_schema(
        request=FinancialItemInputSerializer,
        responses=OrderFinancialItemSerializer,
        examples=[
            OpenApiExample(
                name='Add Revenue Item',
                description='افزودن یک قلم درآمدی جدید به گزارش موجود',
                value={
                    "custom_title": "هزینه فوریت",
                    "amount": "500000",
                    "description": "اضافه شدن خدمات اکسپرس به سفارش"
                }
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='add-item')
    def add_item(self, request, pk=None):
        """ افزودن قلم جدید به درآمد موجود """
        serializer = FinancialItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = self.service.add_item_to_report(request.user, pk, serializer.validated_data)
        return Response(OrderFinancialItemSerializer(item).data)

    @extend_schema(
        request=FinancialItemInputSerializer,
        responses=OrderFinancialItemSerializer,
        examples=[
            OpenApiExample(
                name='Update Revenue Item',
                description='ویرایش مبلغ یا شرح یک قلم درآمدی خاص',
                value={
                    "amount": "14500000",
                    "description": "اصلاح مبلغ واریزی (کسر کارمزد بانکی)",
                    "custom_title": "پیش‌پرداخت نهایی"
                }
            )
        ]
    )
    @action(detail=False, methods=['patch'], url_path='update-item/(?P<item_id>\d+)')
    def update_item(self, request, item_id=None):
        """ ویرایش مستقیم یک قلم درآمدی خاص """
        item = self.service.update_report_item(request.user, item_id, request.data)
        return Response(OrderFinancialItemSerializer(item).data)

    # ===== DELETE SINGLE REVENUE ===== #
    def destroy(self, request, pk=None):
        """ 
        حذف تکی گزارش درآمد.
        """
        self.service.delete_revenue_report(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== DELETE ITEM FROM REVENUE ===== #
    @action(detail=True, methods=['delete'], url_path='items/(?P<item_id>\d+)')
    def delete_item(self, request, pk=None, item_id=None):
        """
        حذف یک قلم خاص از یک گزارش درآمدی.
        چرایی: ممکن است فقط یکی از ردیف‌های درآمد اشتباه باشد، نه کل گزارش.
        """
        self.service.delete_report_item(request.user, item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # ===== DECIDE ON REVENUE (APPROVE/REJECT) ===== #
    @extend_schema(request=ApproveReportInputSerializer)
    @action(detail=True, methods=['post'], url_path='decide')
    def decide(self, request, pk=None):
        """ تایید یا رد درآمد (is_approved = true/false) """
        serializer = ApproveReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.service.decide_on_revenue(
            user=request.user, 
            report_id=pk, 
            approve=serializer.validated_data['approve']
        )
        return Response(status=status.HTTP_200_OK)

    # ===== BULK OPERATIONS ===== #
    @extend_schema(
        request=BulkActionSerializer,
        examples=[
            OpenApiExample(
                name='Bulk Delete Revenues',
                description='حذف همزمان چندین گزارش درآمد (مثلاً اشتباه اپراتور یا تکراری)',
                value={
                    "ids": [105, 106, 110]
                }
            )
        ]
    )
    @extend_schema(request=BulkActionSerializer)
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """ حذف دسته‌جمعی درآمدهای انتخاب شده """
        serializer = BulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.service.bulk_delete_reports(request.user, serializer.validated_data['ids'])
        return Response(status=status.HTTP_204_NO_CONTENT)
