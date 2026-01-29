import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample

from apps.order.models import OrderCostType
from apps.order.services import OrderCostAppService
from ..serializers import (
    OrderCostReportSubmitSerializer, 
    OrderCostReportSerializer,
    OrderCostTypeListSerializer
)

# ================================== #
# ========= SUBMIT REPORT VIEW ========= #
# ================================== #
@extend_schema(
    tags=['Order - Costs'],
    summary="ارسال گزارش هزینه (توسط انبار/چاپ/طراحی)",
    description="""
    این اندپوینت اصلی برای ثبت هزینه‌هاست.
    - برای ارسال فایل و دیتای جیسون همزمان، از فرمت `multipart/form-data` استفاده کنید.
    - فیلد `items` باید یک رشته JSON باشد که لیستی از اقلام را در خود دارد.
    """,
    parameters=[
        OpenApiParameter("id", OpenApiTypes.INT, location=OpenApiParameter.PATH, description="Order ID"),
    ],
    request=OrderCostReportSubmitSerializer,
    responses={201: OrderCostReportSerializer},
    examples=[
        # ===== مثال ۱: هزینه‌های چاپ ===== #
        OpenApiExample(
            'Print Costs Example',
            description='نمونه ثبت هزینه برای بخش چاپ (شامل مواد مصرفی و خدمات)',
            value={
                "title": "گزارش هزینه چاپ (اپراتور ۱)",
                "description": "مصرفی چاپخانه برای سفارش بنر",
                "cost_type_id": 1, # فرض: ID مربوط به چاپ در دیتابیس
                "items": [
                    {
                        # استفاده از آیتم کاتالوگ (مواد اولیه)
                        "catalog_id": 15, 
                        "amount": 150000,
                        "description": "مصرف کاغذ ۳۰۰ گرم"
                    },
                    {
                        # استفاده از آیتم دستی (خدمات)
                        "custom_title": "اجاره دستگاه چاپ دیجیتال",
                        "amount": 50000,
                        "description": "۱ ساعت کارکرد دستگاه"
                    }
                ],
                # "attachments": [] # اگر فایلی هست در multipart ارسال می‌شود
            }
        ),
        # ===== مثال ۲: هزینه‌های حمل و نقل / انبار ===== #
        OpenApiExample(
            'Logistics Costs Example',
            description='نمونه ثبت هزینه برای بخش لجستیک و انبار (بسته‌بندی و ارسال)',
            value={
                "title": "هزینه ارسال و بسته‌بندی سفارش",
                "description": "ارسال به آدرس مشتری در تهران",
                "cost_type_id": 4, # فرض: ID مربوط به حمل و نقل
                "items": [
                    {
                        # هزینه بسته بندی
                        "catalog_id": 22,
                        "amount": 50000,
                        "description": "کارتن ۵ لایه + شلفون"
                    },
                    {
                        # هزینه پیک/باربری
                        "custom_title": "کرایه پیک موتوری",
                        "amount": 120000,
                        "description": "ارسال فوری داخل شهری"
                    }
                ]
            }
        ),
    ]
)
class OrderCostReportSubmitView(GenericAPIView):
    """
    ساخت گزارش هزینه
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCostReportSubmitSerializer
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
        cost_type_id = serializer.validated_data.get('cost_type_id')
        
        try:
            service = OrderCostAppService()
            files = request.FILES.getlist('attachments')
            # ===== 3. Call Service ===== #
            report = service.submit_department_report(
                requester=request.user,
                order_id=pk,
                cost_type_id=cost_type_id,
                validated_data=serializer.validated_data,
                files_list=files
            )
            
            # ===== 4. Return Created Report ===== #
            return Response(
                OrderCostReportSerializer(report).data, 
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ========== ORDER COST TYPE VIEW ========== #
@extend_schema(tags=["Order - Costs"])
class OrderCostTypeView(GenericAPIView):
    """ نمایش لیست نوع هزینه ها """
    serializer_class = OrderCostTypeListSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        cost_types = OrderCostType.objects.all()
        serializer = self.get_serializer(cost_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
