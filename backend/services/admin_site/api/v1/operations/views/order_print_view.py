import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes, extend_schema_view

from apps.order.models  import OrderPrintReport
from apps.order.services import OrderPrintAppService
from ..serializers import PrintReportCreateSerializer, PrintReportDetailSerializer, PrintReportUpdateSerializer

# ========== Examples ========== #
ITEMS_EXAMPLE_CREATE = [
    {
        "material_type": "paper_gloss",
        "price": 150000,
        "custom_title": "کاغذ گلاسه ۳۰۰ گرم",
        "description": "برش دقیق خورده باشد"
    },
    {
        "material_type": "zinc",
        "price": 450000,
        "description": "۴ ورقی"
    }
]

ITEMS_EXAMPLE_UPDATE = [
    {
        "id": 12,
        "material_type": "paper_gloss",
        "description": "تغییر توضیحات آیتم موجود"
    },
    {
        "material_type": "glue",
        "price": 20000,
        "description": "آیتم جدید (بدون ID)"
    }
]

# ========== Order Print Usage Create View ========== #
@extend_schema(
    tags=['Print - Materials'],
    summary="ثبت گزارش مصرف متریال (با فایل)",
    description="""
    **نکته مهم برای فرانت‌‌اند:**
    از آنجایی که فایل آپلود می‌کنید، درخواست باید `multipart/form-data` باشد.
    
    1. فیلد `items`: باید یک آرایه از آبجکت‌ها باشد که **JSON.stringify** شده و به صورت String ارسال شود.
    2. فیلد `attachments`: می‌توانید چندین فایل را با همین نام کلید ارسال کنید.
    """,
    request=PrintReportCreateSerializer,
    responses={
        201: PrintReportDetailSerializer,
        400: OpenApiTypes.OBJECT
    },
    examples=[
        OpenApiExample(
            'Items JSON Structure',
            description='ساختار صحیح JSON که باید Stringify شده و در فیلد items قرار گیرد.',
            value={'items': json.dumps(ITEMS_EXAMPLE_CREATE)},
            request_only=True,
            media_type='multipart/form-data'
        )
    ]
)
class OrderPrintUsageCreateView(GenericAPIView):
    """
    ثبت گزارش مصرف متریال برای چاپ.
    پشتیبانی از آپلود چندین فایل همزمان.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = PrintReportCreateSerializer

    def post(self, request, pk):
        """ 
        pk: شناسه سفارش (Order ID)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = OrderPrintAppService()

            files = serializer.validated_data.get('attachments', [])

            report = service.create_print_usage(
                user=request.user,
                order_id=pk,
                validated_data=serializer.validated_data,
                files_list=files
            )

            return Response(
                PrintReportDetailSerializer(report).data, 
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            # لاگ کردن خطا در محیط پروداکشن ضروری است
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# ========== List View ========== #
@extend_schema(
    tags=['Print - Materials'],
    summary="لیست گزارشات مصرف یک سفارش",
    responses={200: PrintReportDetailSerializer(many=True)}
)
class OrderPrintUsageListView(ListAPIView):
    """ لیست تمام گزارشات ثبت شده برای یک سفارش خاص """
    permission_classes = [IsAuthenticated]
    serializer_class = PrintReportDetailSerializer

    def get_queryset(self):
        return OrderPrintReport.objects.none() 

    def get(self, request, pk):
        """ pk: شناسه سفارش (Order ID) """
        service = OrderPrintAppService()
        reports = service.get_order_print_reports(request.user, order_id=pk)
        
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)

# ========== Print Report Create ========== #
@extend_schema(tags=['Print - Materials'])
@extend_schema_view(
    retrieve=extend_schema(
        summary="مشاهده جزئیات یک گزارش",
        responses={200: PrintReportDetailSerializer}
    ),
    update=extend_schema(
        summary="ویرایش کامل گزارش (جایگزینی)",
        description="""
        قابلیت ویرایش متادیتای گزارش، ویرایش/افزودن اقلام و افزودن فایل جدید.
        برای اقلام (`items`):
        - اگر `id` داشته باشد: آن آیتم آپدیت می‌شود.
        - اگر `id` نداشته باشد: آیتم جدید اضافه می‌شود.
        """,
        request=PrintReportUpdateSerializer,
        responses={200: PrintReportDetailSerializer},
        examples=[
            OpenApiExample(
                'Update Payload Example',
                summary="مثال دیتا برای ویرایش",
                description="توجه کنید items باید stringify شود.",
                value={
                    "title": "عنوان جدید ویرایش شده",
                    "items": json.dumps(ITEMS_EXAMPLE_UPDATE),
                    "attachments": ["(binary file)"]
                },
                request_only=True,
                media_type='multipart/form-data'
            )
        ]
    ),
    partial_update=extend_schema(
        summary="ویرایش جزئی گزارش",
        request=PrintReportUpdateSerializer,
        responses={200: PrintReportDetailSerializer}
    ),
    destroy=extend_schema(
        summary="حذف گزارش مصرف",
        responses={204: None}
    )
)
class OrderPrintUsageDetailView(RetrieveUpdateDestroyAPIView):
    """
    مدیریت تکی گزارشات (مشاهده، ویرایش، حذف).
    ID موجود در URL، شناسه خود گزارش (Report ID) است.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PrintReportUpdateSerializer
        return PrintReportDetailSerializer

    def get_object(self):
        return None 

    def retrieve(self, request, pk=None):
        """ دریافت جزئیات یک گزارش با ID """
        service = OrderPrintAppService()
        try:
            report = service.get_single_report(request.user, report_id=pk)
            return Response(PrintReportDetailSerializer(report).data)
        except Exception:
            return Response({"detail": "گزارش یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, *args, **kwargs):
        """ 
        ویرایش گزارش. 
        فایل‌های ارسالی به فایل‌های قبلی اضافه می‌شوند.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = OrderPrintAppService()
            files = serializer.validated_data.get('attachments', [])
            
            report = service.update_print_usage(
                user=request.user,
                report_id=pk,
                validated_data=serializer.validated_data,
                files_list=files
            )
            
            return Response(PrintReportDetailSerializer(report).data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        """ حذف کامل گزارش و اقلام و فایل‌های وابسته """
        try:
            service = OrderPrintAppService()
            service.delete_print_usage(request.user, report_id=pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
