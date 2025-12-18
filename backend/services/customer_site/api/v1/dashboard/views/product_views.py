from rest_framework import serializers
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes, inline_serializer

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
        این اولین مرحله ساخت محصول است. در اینجا اطلاعات شناسنامه‌ای، تنظیمات کلی قیمت‌گذاری (مثل هزینه ستاپ اولیه) و نیازمندی‌های فایل (مثل اینکه محصول نیاز به طرح رو و پشت دارد) مشخص می‌شود.
        
        **نکات مهم:**
        * در بخش `shell` اطلاعات عمومی قرار می‌گیرد.
        * در بخش `pricing_config` تنظیمات کلی که ربطی به ویژگی‌ها ندارند (مثل هزینه طراحی پایه) قرار می‌گیرند.
        * در `file_requirements` مشخص می‌کنید کاربر چه فایل‌هایی باید آپلود کند (با استفاده از ID مشخصات فایل).
        """,
        request=ProductCoreCreateSerializer,
        responses={201: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Complete Core Example',
                summary='نمونه کامل ساخت محصول کارت ویزیت',
                description='یک محصول کارت ویزیت که نیاز به طرح رو و پشت دارد و دارای تیراژ مشخص است.',
                value={
                    "shell": {
                        "name": "کارت ویزیت لمینت براق",
                        "category": 1,
                        "description": "کارت ویزیت با کیفیت بالا و روکش براق",
                        "has_price": True,
                        "has_quantity": True,
                        "price": "0",  # قیمت پایه صفر، چون قیمت از ویژگی‌ها می‌آید
                        "price_modifier_percent": 0
                    },
                    "pricing_config": {
                        "base_setup_price": 50000,
                        "design_service_available": True,
                        "design_fee": 100000,
                        "allow_custom_quantity": False,
                        "min_quantity": 1000,
                        "max_quantity": 10000
                    },
                    "quantity_ids": [1, 2, 3],  # ID های مدل Quantity
                    "file_requirements": [
                        {"spec_id": 1, "is_required": True},  # مثلا طرح رو
                        {"spec_id": 2, "is_required": True}   # مثلا طرح پشت
                    ]
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

    @extend_schema(request=ProductCoreCreateSerializer)
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
        **منطق بسیار مهم:**
        این متد تمام ویژگی‌های محصول را یکجا مدیریت می‌کند (Bulk Sync). 
        
        شما لیستی از ویژگی‌ها را می‌فرستید. هر ویژگی شامل:
        1. `option_id`: شناسه ویژگی گلوبال (مثلاً جنس کاغذ).
        2. `values_config`: لیستی از مقادیر (مثلاً گلاسه ۳۰۰ گرم، کتان).
        
        **نحوه قیمت دهی:**
        * اگر `global_value_id` بفرستید، یعنی دارید از یک مقدار پیش‌فرض استفاده می‌کنید.
        * `price_impact`: مبلغی که این گزینه به قیمت پایه اضافه می‌کند.
        """,
        request=ProductOptionsBulkSerializer,
        examples=[
            OpenApiExample(
                'Complex Options Scenario',
                summary='سناریوی کامل (جنس کاغذ + سلفون)',
                description='در این مثال، دو ویژگی (جنس کاغذ و نوع روکش) به محصول اضافه می‌شود. برخی مقادیر قیمت دارند و برخی رایگان هستند.',
                value={
                    "options": [
                        # ویژگی اول: جنس کاغذ (ID: 10)
                        {
                            "option_id": 10,
                            "is_required": True,
                            "has_pricing": True,
                            "values_config": [
                                # مقدار اول: گلاسه (ID: 101) - قیمت دارد
                                {
                                    "global_value_id": 101,
                                    "price_impact": 5000,
                                    "is_default": True,
                                    "quantity_step": 1
                                },
                                # مقدار دوم: کتان (ID: 102) - قیمت گران‌تر
                                {
                                    "global_value_id": 102,
                                    "price_impact": 15000,
                                    "is_default": False
                                }
                            ]
                        },
                        # ویژگی دوم: گوشه گرد (ID: 25) - فقط یک حالت دارد (Checkbox)
                        {
                            "option_id": 25,
                            "is_required": False,
                            "has_pricing": True,
                            "values_config": [
                                {
                                    "global_value_id": 505, # بله
                                    "price_impact": 20000,
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
        این متد برای زمانی است که نمی‌خواهید همه آپشن‌ها را دوباره بفرستید و فقط می‌خواهید قیمت‌های یکی را آپدیت کنید.
        """,
        request=OptionConfigUpdateSerializer,
        examples=[
            OpenApiExample(
                'Update Price Example',
                summary='تغییر قیمت‌های ویژگی جنس کاغذ',
                value={
                    "product_option_id": 450,
                    "has_pricing": True,
                    "values": [
                        {
                            "id": 1200,
                            "price_impact": 6000,
                            "is_default": True
                        },
                        {
                            "id": 1201,
                            "price_impact": 18000
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
        ID ویژگی در بدنه درخواست (JSON) ارسال می‌شود.
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
            return Response({'status': 'ویژگی با موقیت بروزرسانی شد.'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== Media Sync API ========== #
    @extend_schema(
        summary="مرحله ۳: اتصال فایل‌ها و تصاویر (Media)",
        description="""
        **منطق فایل‌ها:**
        این متد فایل فیزیکی آپلود نمی‌کند. بلکه فایل‌هایی که قبلاً آپلود شده‌اند را به محصول "وصل" (Link) می‌کند.
        
        **مراحل:**
        1. ابتدا با استفاده از `upload-image` یا `upload-attachment` فایل را آپلود کنید و `ID` بگیرید.
        2. آن `ID`ها را در این متد ارسال کنید.
        
        **کاربرد لیست‌ها:**
        * `attachment_ids_to_link`: لیست ID فایل‌های قالب/پیوست جدید برای اضافه شدن.
        * `attachment_ids_to_unlink`: لیست ID فایل‌هایی که باید از محصول حذف شوند.
        * `image_orders`: لیست ID تمام عکس‌های محصول به ترتیبی که باید نمایش داده شوند (Sort).
        """,
        request=ProductMediaSyncSerializer,
        examples=[
            OpenApiExample(
                'Media Sync Example',
                summary='لینک کردن قالب و مرتب‌سازی عکس‌ها',
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

    # ===== آپلود تصاویر (با اصلاح حیاتی) ===== #
    @extend_schema(
        summary="آپلود تصویر (تکی)",
        request=ProductImageSerializer,
        description=
        """
        آپلود عکس های مربوط به محصولات در این قسمت میتوانید تصاویر را آپلود کنید
        
        تصاویر باید به صورت یک آرایه ارسال شود
        
        مثال: [
            {
                "image": "تصویر محصول"
            },
            {
                "image": "تصویر محصول"
            }
        ]
        نکته مهم: باید حتما id مربوط به محصول رو بدی.
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
            # ===== نمایش پیام ===== #
            return Response(result, status=status.HTTP_202_ACCEPTED)
        
        elif result['status'] == 'completed':
            return Response(result, status=status.HTTP_201_CREATED)
            
        return Response(result, status=status.HTTP_200_OK)

    @extend_schema(
        summary="آپلود فایل در کتابخانه (جهت استفاده در محصولات)",
        request=AttachmentLibrarySerializer,
        description=
        """
        آپلود کردن فایل های پیوست مربوط به محصول
        این قسمت باید به صورت زیر باشه:
        {
            "name": "عنوان فایل",
            "file": "فایل مورد نظر"
        }
        در نظر داشته باش که این قسمت نیازمند ID محصول نیست و در ادامه در قسمت
        sync-media باید ID این فایل  های پیوست رو به صورت لیست ارائه بدی.
        """
    )
    @action(detail=False, methods=['post'], url_path='upload-attachment', parser_classes=[MultiPartParser, FormParser])
    def upload_attachment(self, request):
        """
        این متد فایل را در لینک کردن آنها استفاده میشه آپلود می‌کند تا بعداً توسط ID به محصول لینک شود.
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

    # ===== GET: Retrieve Product Details ===== #
    @extend_schema(responses=ProductDetailSerializer)
    def retrieve(self, request, id=None):
        """ دریافت جزئیات کامل محصول """
        try:
            # سرویس دامین خروجی دیکشنری {product: ..., structured_options: ...} می‌دهد
            data = self.app_service.get_product_detail(id)
            serializer = ProductDetailSerializer(data, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ===== DELETE: Remove Product ===== #
    def destroy(self, request, id=None):
        """ حذف محصول (یا غیرفعال کردن در صورت وابستگی) """
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
    # ========== BULK ACTIONS ========== #
    @extend_schema(
        summary="تغییر وضعیت گروهی محصولات",
        description="""
        فعال یا غیرفعال کردن چندین محصول به صورت همزمان.
        """,
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
        description="""
        حذف چندین محصول به صورت همزمان.
        باید مقدار زیر رو پاس بدی:
        product_ids = [1, 2, 3, 4, 5, ...., n]
        حالت لیست داشته باشه.
        دقت کن که حتما لیستی از اعداد باشه.
        """,
        request=inline_serializer(
            name='BulkDelete',
            fields={
                'product_ids': serializers.ListField(child=serializers.IntegerField())
            }
        ),
        responses={200: OpenApiTypes.OBJECT}
    )
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """ حذف گروهی محصولات """
        product_ids = request.data.get('product_ids', [])

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
