import os

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import (
    extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
)
from drf_spectacular.types import OpenApiTypes
from django.core.files.storage import default_storage
from django.http import FileResponse
from django.utils import timezone
import logging

from apps.dashboard.services import ProductDashboardService
from ..serializers import (
    ProductExportSerializer,
    ProductImportSerializer,
    ExportResponseSerializer,
    ImportResponseSerializer,
    TemplateResponseSerializer,
)

logger = logging.getLogger('dashboard.views.product_export_import')


@extend_schema(tags=['Dashboard-Product-Export-Import'])
class ProductExportImportViewSet(viewsets.ViewSet):
    """
    ViewSet برای مدیریت استخراج و ایمپورت محصولات به/از Excel
    """
    parser_classes = (MultiPartParser, FormParser)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # این سرویس باید ProductExportImportService را هم داشته باشد
        # فعلا از ProductDashboardService استفاده می‌کنیم و بعداً اضافه می‌کنیم
        from apps.dashboard.services.product_service import ProductDashboardService
        self.app_service = ProductDashboardService()
        
        # اضافه کردن سرویس export/import
        from apps.dashboard.services.product_export_import_service import ProductExportImportService
        self.export_import_service = ProductExportImportService()
    
    # ==========================================
    # EXPORT PRODUCTS
    # ==========================================
    
    @extend_schema(
        summary="استخراج محصولات به Excel",
        description="""
        استخراج لیست محصولات به فرمت Excel با چندین Sheet:
        - Sheet 1: اطلاعات اصلی محصولات
        - Sheet 2: فیلدهای داینامیک محصولات
        - Sheet 3: فرمول‌های قیمت‌گذاری
        
        **امکانات:**
        - استخراج همه محصولات یا محصولات انتخابی
        - شامل فیلدهای داینامیک و فرمول‌ها
        - فرمت‌بندی حرفه‌ای Excel
        
        **نکته:** فایل‌های عکس و پیوست در این نسخه استخراج نمی‌شوند (فقط اطلاعات متنی).
        """,
        request=ProductExportSerializer,
        responses={
            200: ExportResponseSerializer,
            400: OpenApiResponse(description="خطا در درخواست"),
            500: OpenApiResponse(description="خطای سرور")
        },
        examples=[
            OpenApiExample(
                name='استخراج همه محصولات',
                summary='استخراج تمام محصولات فعال',
                value={
                    "product_ids": [],
                    "include_fields": True,
                    "include_formulas": True
                },
                request_only=True,
            ),
            OpenApiExample(
                name='استخراج محصولات انتخابی',
                summary='استخراج 3 محصول خاص',
                value={
                    "product_ids": [1, 5, 12],
                    "include_fields": True,
                    "include_formulas": False
                },
                request_only=True,
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='export')
    def export_products(self, request):
        """
        استخراج محصولات به Excel
        """
        serializer = ProductExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_ids = serializer.validated_data.get('product_ids', [])
        include_fields = serializer.validated_data.get('include_fields', True)
        include_formulas = serializer.validated_data.get('include_formulas', True)
        
        try:
            # اگر product_ids خالی باشد، همه محصولات استخراج می‌شوند
            if not product_ids:
                result = self.export_import_service.export_products_to_excel()
            else:
                result = self.export_import_service.export_products_to_excel(product_ids=product_ids)
            
            if not result.get('success'):
                return Response(
                    {'success': False, 'message': result.get('message')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ساخت URL دانلود
            file_path = result.get('file_path')
            file_name = result.get('file_name')
            download_url = request.build_absolute_uri(f'/api/v1/dashboard/products/download/{file_name}')
            
            response_data = {
                'success': True,
                'message': result.get('message'),
                'file_path': file_path,
                'file_name': file_name,
                'product_count': result.get('product_count'),
                'download_url': download_url
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in export_products: {str(e)}", exc_info=True)
            return Response(
                {'success': False, 'message': f'خطا در استخراج: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ==========================================
    # DOWNLOAD EXPORTED FILE
    # ==========================================
    
    @extend_schema(
        summary="دانلود فایل Excel استخراج شده",
        description="دانلود فایل Excel محصولات استخراج شده",
        parameters=[
            OpenApiParameter(
                name='file_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='نام فایل برای دانلود',
                required=True
            )
        ],
        responses={
            200: OpenApiResponse(description="فایل Excel"),
            404: OpenApiResponse(description="فایل یافت نشد")
        }
    )
    @action(detail=False, methods=['get'], url_path='download/(?P<file_name>[^/]+)')
    def download_export(self, request, file_name=None):
        """
        دانلود فایل Excel استخراج شده
        """
        try:
            file_path = f"exports/products/{file_name}"
            
            if not default_storage.exists(file_path):
                return Response(
                    {'success': False, 'message': 'فایل یافت نشد.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # باز کردن فایل
            file = default_storage.open(file_path, 'rb')
            response = FileResponse(
                file,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            response['Content-Length'] = default_storage.size(file_path)
            
            return response
            
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}", exc_info=True)
            return Response(
                {'success': False, 'message': f'خطا در دانلود: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ==========================================
    # IMPORT PRODUCTS
    # ==========================================
    
    @extend_schema(
        summary="ایمپورت محصولات از Excel",
        description="""
        ایمپورت محصولات از فایل Excel.
        
        **قوانین:**
        - فایل باید با فرمت .xlsx باشد
        - ستون‌های اجباری: نام محصول
        - محصولات تکراری (بر اساس نام) نادیده گرفته می‌شوند مگر اینکه `update_existing=true` باشد
        - در صورت خطا در برخی سطرها، بسته به `skip_errors` یا متوقف می‌شود یا ادامه می‌دهد
        
        **نکته:** در این نسخه، ایمپورت فقط اطلاعات پایه محصول را انجام می‌دهد.
        فیلدهای داینامیک، فرمول‌ها، عکس‌ها و پیوست‌ها باید بعداً اضافه شوند.
        """,
        request=ProductImportSerializer,
        responses={
            200: ImportResponseSerializer,
            400: OpenApiResponse(description="خطا در فایل یا داده‌ها"),
            500: OpenApiResponse(description="خطای سرور")
        },
        examples=[
            OpenApiExample(
                name='ایمپورت با به‌روزرسانی',
                summary='ایمپورت و به‌روزرسانی محصولات تکراری',
                value={
                    "file": "products.xlsx",
                    "update_existing": True,
                    "skip_errors": True
                },
                request_only=True,
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='import')
    def import_products(self, request):
        """
        ایمپورت محصولات از Excel
        """
        serializer = ProductImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uploaded_file = serializer.validated_data.get('file')
        update_existing = serializer.validated_data.get('update_existing', False)
        skip_errors = serializer.validated_data.get('skip_errors', True)
        
        try:
            # ذخیره فایل آپلود شده
            file_path = f"uploads/products/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
            
            # اطمینان از وجود پوشه
            uploads_dir = os.path.join(default_storage.location, 'uploads', 'products')
            os.makedirs(uploads_dir, exist_ok=True)
            
            # ذخیره فایل
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
            default_storage.save(file_path, uploaded_file)
            
            # فراخوانی سرویس ایمپورت (با ارسال کاربر)
            result = self.export_import_service.import_products_from_excel(file_path, user=request.user)
            
            # حذف فایل موقت
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
            
            response_data = {
                'success': result.get('success'),
                'message': result.get('message'),
                'imported_count': result.get('imported_count'),
                'failed_count': result.get('failed_count'),
                'errors': result.get('errors', [])
            }
            
            if not result.get('success'):
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in import_products: {str(e)}", exc_info=True)
            return Response(
                {'success': False, 'message': f'خطا در ایمپورت: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ==========================================
    # GET EXPORT HISTORY (Optional)
    # ==========================================
    
    @extend_schema(
        summary="لیست فایل‌های استخراج شده",
        description="دریافت لیست فایل‌های Excel استخراج شده اخیر",
        responses={
            200: OpenApiResponse(description="لیست فایل‌ها"),
            500: OpenApiResponse(description="خطای سرور")
        }
    )
    @action(detail=False, methods=['get'], url_path='history')
    def export_history(self, request):
        """
        لیست فایل‌های استخراج شده اخیر
        """
        try:
            # لیست فایل‌های exports/products
            files = []
            if default_storage.exists('exports/products'):
                all_files = default_storage.listdir('exports/products')[1]  # [0] = directories, [1] = files
                for file_name in sorted(all_files, reverse=True)[:20]:  # آخرین 20 فایل
                    file_path = f"exports/products/{file_name}"
                    files.append({
                        'file_name': file_name,
                        'file_path': file_path,
                        'size': default_storage.size(file_path),
                        'created_at': default_storage.get_modified_time(file_path).strftime('%Y-%m-%d %H:%M'),
                        'download_url': request.build_absolute_uri(f'/api/v1/dashboard/products/download/{file_name}')
                    })
            
            return Response({
                'success': True,
                'files': files
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting export history: {str(e)}", exc_info=True)
            return Response(
                {'success': False, 'message': f'خطا در دریافت تاریخچه: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )