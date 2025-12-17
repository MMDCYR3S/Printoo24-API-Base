import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from apps.operations.services import OrderCostAppService
from ..serializers import (
    OrderCostReportSubmitSerializer, 
    OrderCostReportSerializer,
)

# ========================================== #
# ========== 1. SUBMIT REPORT VIEW ========= #
# ========================================== #

@extend_schema(
    tags=['Order - Costs (Operations)'],
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
    responses={201: OrderCostReportSerializer}
)
class OrderCostReportSubmitView(GenericAPIView):
    """
    جایگزین ویوهای قدیمی CreateSheet و AddItems.
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
        
        try:
            service = OrderCostAppService()
            files = request.FILES.getlist('attachments')
            
            # ===== 3. Call Service ===== #
            report = service.submit_department_report(
                requester=request.user,
                order_id=pk,
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
