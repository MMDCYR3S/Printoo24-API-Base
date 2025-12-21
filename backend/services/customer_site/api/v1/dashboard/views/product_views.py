from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes, inline_serializer
from rest_framework import serializers

# ===== ایمپورت سرویس‌ها و سریالایزرها ===== #
from apps.dashboard.services import ProductDashboardService
from ..serializers import (
    ProductCoreCreateSerializer,
    ProductOptionsBulkSerializer,
    ProductMediaSyncSerializer,
    ProductImageSerializer,
    AttachmentLibrarySerializer,
    ProductDetailSerializer,
    OptionConfigUpdateSerializer,
    ProductSerializer,
)

# ===== Product Dashboard View Set ===== #
@extend_schema(tags=['Dashboard-Product-Refactored'])
class ProductDashboardViewSet(viewsets.ViewSet):
    """
    مدیریت محصول با معماری ۳-مرحله‌ای (Core, Options, Media).
    این ویو کنترل‌کننده اصلی منطق بیزنس محصولات در پنل ادمین است.
    """
    lookup_field = 'id'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_service = ProductDashboardService()

    # ========== Core Product API Create ========== #
    def list(self, request):
        """ نمایش لیست محصولات """
        try:
            products = self.app_service.get_all_products() 
            serializer = ProductSerializer(products, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"خطا در دریافت لیست محصولات: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="مرحله ۱: ایجاد اطلاعات پایه محصول",
        description="""
        **توضیحات:**
        این اولین مرحله ساخت محصول است. در اینجا اطلاعات شناسنامه‌ای (Shell) و تنظیمات کلی (Config) دریافت می‌شود.
        
        **نکات ساختاری:**
        * `shell`: شامل نام، اسلاگ، دسته‌بندی و قیمت پایه است.
        * `pricing_config`: تنظیمات ستاپ و هزینه‌های جانبی که به ویژگی‌ها ربطی ندارد.
        * `quantity_ids`: لیست IDهای تیراژهای مجاز برای این محصول.
        """,
        request=ProductCoreCreateSerializer,
        responses={201: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Create Product Core Example',
                summary='نمونه ساخت محصول (تراکت تبلیغاتی)',
                description='ایجاد یک محصول با قیمت پایه صفر (قیمت از ویژگی‌ها می‌آید) و هزینه طراحی.',
                value={
                    "shell": {
                        "name": "تراکت گلاسه ۱۳۵ گرم",
                        "category": 1,
                        "description": "تراکت تبلیغاتی با کیفیت چاپ افست",
                        "has_price": True,
                        "price": "0",
                        "has_quantity": True,
                        "price_per_unit": 1000,
                        "is_active": True
                    },
                    "pricing_config": {
                        "base_setup_price": 50000,
                        "design_service_available": True,
                        "design_fee": 150000,
                        "allow_custom_quantity": False,
                        "min_quantity": 1000,
                        "max_quantity": 50000,
                        "accepts_custom_dimensions": False
                    },
                    "quantity_ids": [1, 2, 3, 4]
                },
                request_only=True,
            )
        ]
    )
    def create(self, request):
        """ مرحله اول: ایجاد محصول با تمام مشخصات پایه """
        serializer = ProductCoreCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product = self.app_service.create_full_product_core(request.user, serializer.validated_data)
        
        # ===== نمایش پیام ===== #
        return Response({'id': product.id, 'message': 'اطلاعات پایه محصول با موفقیت ایجاد شدند.'}, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="ویرایش اطلاعات پایه محصول",
        request=ProductCoreCreateSerializer,
        examples=[
             OpenApiExample(
                'Update Product Core Example',
                summary='نمونه ویرایش نام و قیمت پایه',
                value={
                    "shell": {
                        "name": "تراکت گلاسه ۱۳۵ گرم (ویرایش شده)",
                        "category": 1,
                        "has_price": True,
                        "price": "1000",
                        "has_quantity": True,
                        "price_per_unit": 1000,
                        "is_active": True
                    },
                    "pricing_config": {
                        "base_setup_price": 60000
                    },
                    "quantity_ids": [1, 5]
                },
                request_only=True,
            )
        ]
    )
    def update(self, request, id=None):
        """ ویرایش کلی اطلاعات پایه """
        serializer = ProductCoreCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        self.app_service.update_full_product_core(id, serializer.validated_data)
        return Response({'status': 'Product core updated'})

    # ========== Option and Pricing API ========== #
    @extend_schema(
        summary="مرحله ۲: همگام‌سازی ویژگی‌ها (Options)",
        description="""
        **منطق:**
        اتصال ویژگی‌های گلوبال به این محصول خاص.
        
        **ساختار دیتا:**
        * `option_id`: شناسه ویژگی در بانک ویژگی‌ها.
        * `values_config`: لیستی از مقادیری که می‌خواهید فعال کنید.
        * `global_value_id`: شناسه مقدار در بانک مقادیر.
        """,
        request=ProductOptionsBulkSerializer,
        examples=[
            OpenApiExample(
                'Bulk Options Sync Example',
                summary='اتصال جنس کاغذ و نوع روکش',
                description='در اینجا ویژگی جنس کاغذ (ID:10) و روکش (ID:12) را به محصول متصل می‌کنیم.',
                value={
                    "options": [
                        {
                            "option_id": 10,
                            "is_required": True,
                            "has_pricing": True,
                            "values_config": [
                                {
                                    "global_value_id": 101,
                                    "price_impact": "5000",
                                    "is_default": True,
                                    "is_active": True
                                },
                                {
                                    "global_value_id": 102,
                                    "price_impact": "15000",
                                    "is_default": False,
                                    "is_active": True
                                }
                            ]
                        },
                        {
                            "option_id": 12,
                            "is_required": False,
                            "has_pricing": True,
                            "values_config": [
                                {
                                    "global_value_id": 201,
                                    "price_impact": "20000",
                                    "is_default": False
                                }
                            ]
                        }
                    ]
                },
                request_only=True
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='options')
    def sync_options(self, request, id=None):
        """ مرحله دوم: ارسال لیست تمام آپشن‌ها و قیمت‌هایشان """
        serializer = ProductOptionsBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        results = self.app_service.bulk_sync_options(
            product_id=id, 
            options_data=serializer.validated_data['options']
        )
        return Response({'results': results}, status=status.HTTP_200_OK)
    
    # ========== UPDATE Option Config ========== #
    @extend_schema(
        summary="ویرایش تنظیمات یک ویژگی خاص",
        description="""
        **تفاوت با متد قبلی:**
        این متد برای زمانی است که ویژگی قبلاً وصل شده و فقط می‌خواهید قیمت‌ها یا تنظیمات `ProductOptionValue` را تغییر دهید.
        
        **نکته مهم:**
        در لیست `values` باید `id` را بفرستید که مربوط به `ProductOptionValue` (جدول واسط) است، نه `GlobalOptionValue`.
        """,
        request=OptionConfigUpdateSerializer,
        examples=[
            OpenApiExample(
                'Update Specific Option Config',
                summary='تغییر قیمت گلاسه برای این محصول',
                value={
                    "product_option_id": 450,
                    "is_required": True,
                    "has_pricing": True,
                    "values": [
                        {
                            "id": 1200, 
                            "price_impact": "7500",
                            "is_default": True,
                            "order": 1
                        },
                        {
                            "id": 1201,
                            "price_impact": "18000",
                            "is_default": False,
                            "order": 2
                        }
                    ]
                }
            )
        ]
    )
    @action(detail=True, methods=['patch'], url_path='update-option-config')
    def update_option_config(self, request, id=None):
        """
        ویرایش تنظیمات ویژگی.
        """
        serializer = OptionConfigUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            self.app_service.update_option_configuration(
                product_id=id,
                option_id=data['product_option_id'],
                data=data
            )
            return Response({'status': 'ویژگی با موفقیت بروزرسانی شد.'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== Media Sync API ========== #
    @extend_schema(
        summary="مرحله ۳: اتصال فایل‌ها و تصاویر (Media)",
        description="""
        **وظیفه:**
        اتصال فایل‌های آپلود شده (در مرحله قبل) به محصول و مرتب‌سازی تصاویر.
        """,
        request=ProductMediaSyncSerializer,
        examples=[
            OpenApiExample(
                'Media Link & Sort Example',
                summary='لینک کردن قالب لایه باز و مرتب‌سازی عکس‌ها',
                value={
                    "attachment_ids_to_link": [15, 16],
                    "attachment_ids_to_unlink": [10],
                    "image_orders": [102, 105, 101]
                },
                request_only=True
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='media-sync')
    def sync_media(self, request, id=None):
        """ لینک کردن اطلاعات پیوست‌ها و تصاویر. """
        serializer = ProductMediaSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.app_service.sync_media_assets(
            product_id=id, 
            user=request.user,
            data=serializer.validated_data
        )
        return Response({'status': 'فایل های پیوست با موفقیت به روز شد'})

    # ===== آپلود تصاویر ===== #
    @extend_schema(
        summary="آپلود تصویر (تکی)",
        request=ProductImageSerializer,
        description="""
        تصویر محصول را آپلود کنید. این متد تصویر را ذخیره کرده و یک ID برمی‌گرداند.
        این ID باید در متد `sync-media` برای مرتب‌سازی استفاده شود.
        """
    )
    @action(detail=True, methods=['post'], url_path='upload-image', parser_classes=[MultiPartParser, FormParser, JSONParser])
    def upload_image(self, request, id=None):
        """ آپلود عکس محصول """
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({'image': 'File required'}, status=status.HTTP_400_BAD_REQUEST)

        # ===== آپلود تصاویر ===== #
        result = self.app_service.upload_product_image_async(
            product_id=id,
            user=request.user,
            file_obj=file_obj
        )
        
        # ===== بررسی نتایج ===== #
        if result['status'] == 'processing':
            return Response(result, status=status.HTTP_202_ACCEPTED)
        
        elif result['status'] == 'completed':
            return Response(result, status=status.HTTP_201_CREATED)
            
        return Response(result, status=status.HTTP_200_OK)

    @extend_schema(
        summary="آپلود فایل در کتابخانه (جهت استفاده در محصولات)",
        request=AttachmentLibrarySerializer,
        description="""
        آپلود فایل‌های جانبی (مانند قالب‌های لایه باز یا راهنمای طراحی).
        خروجی شامل ID فایل است که باید در متد `sync-media` در لیست `attachment_ids_to_link` قرار گیرد.
        """
    )
    @action(detail=False, methods=['post'], url_path='upload-attachment', parser_classes=[MultiPartParser, FormParser])
    def upload_attachment(self, request):
        """
        آپلود فایل برای لینک کردن بعدی.
        """
        file_obj = request.FILES.get('file')
        name = request.data.get('name')
        
        if not file_obj or not name:
            return Response({'detail': 'File and name are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # فراخوانی متد سرویس
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

    # ===== GET: Retrieve Product Details ===== #
    @extend_schema(responses=ProductDetailSerializer)
    def retrieve(self, request, id=None):
        """ دریافت جزئیات کامل محصول """
        try:
            data = self.app_service.get_product_detail(id)
            serializer = ProductDetailSerializer(data, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ===== DELETE: Remove Product ===== #
    def destroy(self, request, id=None):
        """ حذف محصول """
        self.app_service.delete_product(id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== DELETE Option (Detach) ===== #
    @extend_schema(summary="حذف یک ویژگی از محصول")
    @action(detail=True, methods=['delete'], url_path='options/(?P<option_id>\d+)')
    def remove_option(self, request, id=None, option_id=None):
        """ 
        حذف ویژگی از محصول.
        option_id: شناسه ProductOption (نه ویژگی گلوبال).
        """
        try:
            self.app_service.remove_option_from_product(id, option_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== BULK ACTIONS ========== #
    @extend_schema(
        summary="تغییر وضعیت گروهی محصولات",
        request=inline_serializer(
            name='BulkStatusUpdate',
            fields={
                'product_ids': serializers.ListField(child=serializers.IntegerField()),
                'is_active': serializers.BooleanField()
            }
        ),
        responses={200: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Activate Products',
                value={'product_ids': [10, 12, 15], 'is_active': True},
                request_only=True
            )
        ]
    )
    @action(detail=False, methods=['patch'], url_path='bulk-status')
    def bulk_update_status(self, request):
        """ تغییر وضعیت گروهی (Active/Inactive) """
        product_ids = request.data.get('product_ids', [])
        is_active = request.data.get('is_active')

        if not product_ids or is_active is None:
            return Response(
                {'error': 'product_ids and is_active are required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            count = self.app_service.bulk_update_product_status(product_ids, is_active)
            return Response(
                {'message': f'{count} محصول با موفقیت بروزرسانی شدند.', 'updated_count': count},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="حذف گروهی محصولات",
        request=inline_serializer(
            name='BulkDelete',
            fields={
                'product_ids': serializers.ListField(child=serializers.IntegerField())
            }
        ),
        responses={200: OpenApiTypes.OBJECT},
        examples=[
             OpenApiExample(
                'Bulk Delete Example',
                value={'product_ids': [5, 6, 7]},
                request_only=True
            )
        ]
    )
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """ حذف گروهی محصولات """
        data = request.data
        product_ids = []

        if isinstance(data, list):
            product_ids = data
        elif isinstance(data, dict):
            product_ids = data.get('product_ids', [])

        if not product_ids:
            return Response(
                {'error': 'product_ids is required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = self.app_service.bulk_delete_products(product_ids)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
