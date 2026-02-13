import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample

from apps.order.models import OrderFinancialType
from apps.order.services import OrderFinancialAppService
from ..serializers import (
    OrderFinancialReportSubmitSerializer, 
    OrderFinancialReportSerializer,
    OrderFinancialTypeListSerializer
)

# ====================================== #
# ========= SUBMIT REPORT VIEW ========= #
# ====================================== #
@extend_schema(
    tags=['Financial Report'],
    summary="ارسال گزارش هزینه (توسط انبار/چاپ/طراحی)",
    description="""
    این اندپوینت اصلی برای ثبت هزینه‌هاست.
    """,
    request=OrderFinancialReportSubmitSerializer,
    responses={201: OrderFinancialReportSerializer},
    examples=[
        # ===== مثال ۱: هزینه‌های چاپ ===== #
        OpenApiExample(
            'Print Financials Example',
            description='نمونه ثبت هزینه بخش چاپ',
            value={
                "title": "هزینه زینک و کپی",
                "financial_tag_id": 1,
                "items": [
                    {
                        "catalog_id": 5, 
                        "amount": 250000,
                        "description": "خرید زینک GTO"
                    }
                ],
                "attachments": [
                    "File_1",
                    "File_2"
                ]
            }
        ),
        # ===== مثال ۲: هزینه‌های حمل و نقل / انبار ===== #
        OpenApiExample(
            'Logistics Financials Example',
            description='نمونه ثبت هزینه برای بخش لجستیک و انبار (بسته‌بندی و ارسال)',
            value={
                "title": "هزینه ارسال و بسته‌بندی سفارش",
                "description": "ارسال به آدرس مشتری در تهران",
                "financial_tag_id": 4,
                "items": [
                    {
                        "catalog_id": 22,
                        "amount": 50000,
                        "description": "کارتن ۵ لایه + شلفون"
                    },
                    {
                        "custom_title": "کرایه پیک موتوری",
                        "amount": 120000,
                        "description": "ارسال فوری داخل شهری"
                    }
                ],
                "attachments": [
                    "File_1",
                    "File_2"
                ]
            }
        ),
    ]
)
class OrderFinancialReportSubmitView(GenericAPIView):
    """
    ساخت گزارش هزینه
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderFinancialReportSubmitSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser] 

    def post(self, request, pk):
        """ 
        pk: Order ID 
        """
        # ===== 1. Pre-process Data for Multipart ===== #
        data = request.data.copy()
        if 'items' in data and isinstance(data['items'], str):
            try:
                data['items'] = json.loads(data['items'])
            except ValueError:
                return Response({"items": ["فرمت JSON نامعتبر است."]}, status=status.HTTP_400_BAD_REQUEST)

        # ===== 2. Validate Input ===== #
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        financial_tag_id = serializer.validated_data.get('financial_tag_id')
        
        try:
            service = OrderFinancialAppService()
            files = request.FILES.getlist('attachments')

            # ===== 3. Call Service ===== #
            report = service.submit_department_report(
                requester=request.user,
                order_id=pk,
                financial_tag_id=financial_tag_id,
                validated_data=serializer.validated_data,
                attachments=files
            )
            
            # ===== 4. Return Created Report ===== #
            return Response(
                OrderFinancialReportSerializer(report).data, 
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ========== ORDER COST TYPE VIEW ========== #
@extend_schema(tags=["Financial Report"])
class OrderFinancialTypeView(GenericAPIView):
    """ نمایش لیست نوع هزینه ها """
    serializer_class = OrderFinancialTypeListSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        financial_tags = OrderFinancialType.objects.all()
        serializer = self.get_serializer(financial_tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
