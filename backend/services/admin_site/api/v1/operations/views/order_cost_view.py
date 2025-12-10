from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema

from apps.operations.services import OrderCostAppService
from ..serializers import (
    OrderCostReportCreateSerializer, 
    OrderCostReportDetailSerializer
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
            
            report = service.create_report(
                requester=request.user,
                order_id=pk,
                validated_data=serializer.validated_data,
                file_data=serializer.validated_data.get('attachment')
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
