from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema

from apps.dashboard.services import ProductDashboardService
from ..serializers import (
    ProductCoreCreateSerializer,
    ProductOptionsBulkSerializer,
    ProductMediaSyncSerializer,
    ProductImageSerializer,
    AttachmentLibrarySerializer
)

# ===== Product Dashboard View Set ===== #
@extend_schema(tags=['Dashboard-Product-Refactored'])
class ProductDashboardViewSet(viewsets.ViewSet):
    """
    مدیریت محصول با معماری ۳-مرحله‌ای (Core, Options, Media).
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_service = ProductDashboardService()

    # ===== Core API ===== #
    @extend_schema(request=ProductCoreCreateSerializer, responses=ProductCoreCreateSerializer)
    def create(self, request):
        """ مرحله اول: ایجاد محصول با تمام مشخصات پایه """
        serializer = ProductCoreCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product = self.app_service.create_full_product_core(request.user, serializer.validated_data)
        
        # ===== نمایش پیام ===== #
        return Response({'id': product.id, 'message': 'اطلاعات پایه محصول با موفقیت ایجاد شدند.'}, status=status.HTTP_201_CREATED)

    @extend_schema(request=ProductCoreCreateSerializer)
    def update(self, request, pk=None):
        """ ویرایش کلی اطلاعات پایه """
        serializer = ProductCoreCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        self.app_service.update_full_product_core(pk, serializer.validated_data)
        return Response({'status': 'Product core updated'})

    # ===== Option API ===== #
    @extend_schema(request=ProductOptionsBulkSerializer, summary="مدیریت تمام ویژگی‌ها")
    @action(detail=True, methods=['post'], url_path='options')
    def sync_options(self, request, pk=None):
        """ مرحله دوم: ارسال لیست تمام آپشن‌ها و قیمت‌هایشان """
        serializer = ProductOptionsBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        results = self.app_service.bulk_sync_options(
            product_id=pk, 
            options_data=serializer.validated_data['options']
        )
        return Response({'results': results}, status=status.HTTP_200_OK)

    # ===== Media API ===== #
    @extend_schema(request=ProductMediaSyncSerializer, summary="مدیریت لینک فایل‌ها و ترتیب عکس‌ها")
    @action(detail=True, methods=['post'], url_path='media-sync')
    def sync_media(self, request, pk=None):
        """ مرحله سوم (بخش اول): لینک فایل‌ها و ترتیب تصاویر """
        serializer = ProductMediaSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.app_service.sync_media_assets(
            product_id=pk, 
            user=request.user,
            data=serializer.validated_data
        )
        return Response({'status': 'فایل های پیوست با موفقیت به روز شد'})

    # ===== آپلود تصاویر (با اصلاح حیاتی) ===== #
    @extend_schema(summary="آپلود تصویر (تکی)", request=ProductImageSerializer)
    @action(detail=True, methods=['post'], url_path='upload-image', parser_classes=[MultiPartParser, FormParser, JSONParser])
    def upload_image(self, request, pk=None):
        """ 
        مرحله سوم (بخش دوم): آپلود فیزیکی تصاویر.
        این متد از صفсинک/Async هوشمند استفاده می‌کند.
        """
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({'image': 'File required'}, status=status.HTTP_400_BAD_REQUEST)

        # ===== آپلود تصاویر ===== #
        result = self.app_service.upload_product_image_async(
            product_id=pk,
            user=request.user,
            file_obj=file_obj
        )
        
        # ===== بررسی نتایج ===== #
        if result['status'] == 'processing':
            # ===== نمایش پیام ===== #
            return Response(result, status=status.HTTP_202_ACCEPTED)
        
        elif result['status'] == 'completed':
            return Response(result, status=status.HTTP_201_CREATED)
            
        return Response(result, status=status.HTTP_200_OK)

    @extend_schema(summary="آپلود فایل در کتابخانه (جهت استفاده در محصولات)", request=AttachmentLibrarySerializer)
    @action(detail=False, methods=['post'], url_path='upload-attachment', parser_classes=[MultiPartParser, FormParser])
    def upload_attachment(self, request):
        """
        این متد فایل را در Attachment Library آپلود می‌کند تا بعداً توسط ID به محصول لینک شود.
        """
        file_obj = request.FILES.get('file')
        name = request.data.get('name')
        
        if not file_obj or not name:
            return Response({'detail': 'File and name are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # فراخوانی متد سرویس (Async/Sync)
        result = self.app_service.upload_attachment_library_async(
            user=request.user,
            file_obj=file_obj,
            name=name
        )
        
        if result['status'] == 'processing':
            return Response(result, status=status.HTTP_202_ACCEPTED)
        elif result['status'] == 'completed':
            return Response(result, status=status.HTTP_201_CREATED)
            
        return Response(result, status=status.HTTP_200_OK)
