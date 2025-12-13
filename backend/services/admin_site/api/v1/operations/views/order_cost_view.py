from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema

from apps.operations.services import OrderCostAppService
from ..serializers import (
    OrderCostReportCreateSerializer, OrderCostReportDetailSerializer,
    CostTypeInputSerializer, CostTypeDetailSerializer
)

# ========== Order Cost Report Create View ========== #
@extend_schema(
    tags=['Order-Costs'],
    description="""
    ایجاد یک گزارش مالی جدید شامل چندین ریز هزینه.
    پشتیبانی از آپلود فایل (Multipart).\n
    در قسمت مربوط به id، باید شناسه سفارش (Order ID) قرار گیرد.\n
    مثال:\n
    
    API -> POST -> /api/v1/operations/costs/reports/10/
    {
        "title": "گزارش ضایعات چاپ افست",
        "description": "به دلیل قطع برق در حین کار، بخشی از فرم‌های چاپی باطله شد.",
        "is_approved_by_finance": false,
        "finance_note": "",
        "created_by_name": "علی محمدی (اپراتور چاپ)",
        "created_at": "2025-12-10T14:30:00Z",
        "items": [
            {
                "catalog_id": 1,
                "custom_title": null,
                "title_display": "کاغذ گلاسه ۳۰۰ گرم (GL-300) - مات", 
                "cost_type_display": "مواد اولیه",
                "amount": 3000000,
                "description": "۵۰۰ برگ ضایعات"
            },
            {
                "catalog_id": null,
                "custom_title": "سرویس تعمیرکار برق",
                "title_display": "سرویس تعمیرکار برق",
                "cost_type_display": "سایر",
                "amount": 500000,
                "description": "پرداخت به آقای حسینی بابت وصل مجدد تابلو برق"
            }
        ]
    }
    """               
)
class OrderCostReportCreateView(GenericAPIView):
    """
    ایجاد یک گزارش مالی جدید شامل چندین ریز هزینه.
    پشتیبانی از آپلود فایل (Multipart).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCostReportCreateSerializer
    # ===== تنظیمات پارسر برای آپلود فایل ===== #
    parser_classes = [MultiPartParser, FormParser, JSONParser] 

    def post(self, request, pk):
        """
        pk: شناسه سفارش (Order ID)
        """
        # ===== اعتبارسنجی ورودی ===== #
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # ===== ایجاد سرویس و ثبت گزارش ===== #
            service = OrderCostAppService()
            
            files = serializer.validated_data.get('attachments', [])
            
            report = service.create_report(
                requester=request.user,
                order_id=pk,
                validated_data=serializer.validated_data,
                file_data=files
            )
            
            # ===== آماده‌سازی خروجی ===== #
            output_serializer = OrderCostReportDetailSerializer(report, context={'request': request})
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            from rest_framework.exceptions import ValidationError, PermissionDenied
            if isinstance(e, (ValidationError, PermissionDenied)):
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response(
                {"detail": "خطای سیستمی در ثبت گزارش.", "error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Order Cost ViewSet ========== #
@extend_schema(tags=['Order - CostType'])
class CostTypeViewSet(ModelViewSet):
    """
    مدیریت انواع هزینه‌ها.
    ریفکتور شده با استفاده از ModelViewSet برای کاهش کدنویسی تکراری.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OrderCostAppService()

    def get_queryset(self):
        """
        اتصال ویوست به سرویس برای دریافت لیست.
        با این کار، متدهای list و retrieve به صورت خودکار کار می‌کنند.
        """
        return self.service.list_cost_types(self.request.user)

    def get_serializer_class(self):
        """ مدیریت هوشمند سریالایزرهای ورودی و خروجی """
        if self.action in ['create', 'update', 'partial_update']:
            return CostTypeInputSerializer
        return CostTypeDetailSerializer

    def create(self, request, *args, **kwargs):
        """ 
        بازنویسی create برای اتصال به سرویس دامین.
        چون ModelViewSet به صورت پیش‌فرض serializer.save() می‌کند، ولی ما می‌خواهیم
        service.create_cost_type() صدا زده شود.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cost_type = self.service.create_cost_type(request.user, serializer.validated_data)

        output_serializer = CostTypeDetailSerializer(cost_type)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """ بازنویسی update برای اتصال به سرویس """
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        pk = kwargs.get('pk')
        cost_type = self.service.update_cost_type(request.user, pk, serializer.validated_data)

        output_serializer = CostTypeDetailSerializer(cost_type)
        return Response(output_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """ بازنویسی destroy برای استفاده از سرویس حذف (جهت چک کردن وابستگی‌ها) """
        pk = kwargs.get('pk')
        self.service.delete_cost_type(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
