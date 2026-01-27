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
    مدیریت جامع محصولات (نسخه ۳ لایه).
    شامل تعریف هسته، تنظیمات قیمت، ویژگی‌ها و مدیا.
    """
    lookup_field = 'id'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_service = ProductDashboardService()

    # ========== LIST ========== #
    def list(self, request):
        """ نمایش لیست خلاصه محصولات """
        try:
            products = self.app_service.get_all_products() 
            serializer = ProductSerializer(products, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"خطا در دریافت لیست محصولات: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ========== CREATE CORE ========== #
    @extend_schema(
        summary="مرحله ۱: ایجاد محصول (هسته + قیمت + تیراژ + سایز)",
        description="""
        **توضیحات:**
        این متد قلب تعریف محصول است. شما می‌توانید همزمان:
        1. اطلاعات شناسنامه‌ای (نام، کد، اسلاگ) را تعریف کنید.
        2. استراتژی قیمت‌گذاری (تیراژدار یا متری/تعدادی) را مشخص کنید.
        3. سایزها و تیراژهای مجاز را به همراه قیمت و راهنما (Guide) ثبت کنید.
        
        **نکات کلیدی:**
        * اگر `has_quantity=True`: باید لیست `quantities` پر شود.
        * اگر `has_quantity=False`: باید `price_per_unit` و `min_quantity` در کانفیگ تنظیم شود.
        * فیلدهای `guide_text` و `guide_type` برای تمام بخش‌ها (محصول، سایز، تیراژ) قابل استفاده است.
        """,
        request=ProductCoreCreateSerializer,
        responses={201: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Scenario 1: Offset Printing (With Quantity)',
                summary='سناریو ۱: محصول چاپ افست (دارای تیراژ و سایز ثابت)',
                description='مثال برای کارت ویزیت که فقط در تیراژهای ۱۰۰۰ و ۲۰۰۰ و سایزهای مشخص فروخته می‌شود.',
                value={
                    "shell": {
                        "name": "کارت ویزیت لمینت براق",
                        "category_id": 1,
                        "description": "...",
                        "has_price": True,
                        "price": "0",
                        "has_quantity": True,
                        "is_active": True,
                        "guide_text": "زمان تحویل این محصول ۷ روز کاری است.",
                        "guide_type": "warning"
                    },
                    "pricing_config": {
                        "base_setup_price": 0,
                        "design_service_available": True,
                        "design_fee": 150000
                    },
                    "quantities": [
                        {
                            "id": 10,
                            "guide_text": "پرفروش‌ترین",
                            "guide_type": "tip"
                        },
                        {
                            "id": 11,
                            "guide_text": "",
                            "guide_type": "info"
                        }
                    ],
                    "sizes": [
                        { 
                            "id": 1, # سایز استاندارد (9x5)
                            "price_impact": 0 
                        },
                        { 
                            "id": 2, # سایز دورگرد (Add-on price)
                            "price_impact": 50000,
                            "guide_text": "قالب برش خاص دارد",
                            "guide_type": "info"
                        }
                    ]
                },
                request_only=True,
            ),
            OpenApiExample(
                'Scenario 2: Digital Printing (No Quantity)',
                summary='سناریو ۲: چاپ دیجیتال/بنر (بدون تیراژ ثابت)',
                description='مثال برای بنر که قیمت بر اساس متر محیط یا تعداد دلخواه کاربر محاسبه می‌شود.',
                value={
                    "shell": {
                        "name": "بنر مناسبتی (محاسبه متری)",
                        "category_id": 1,
                        "has_price": True,
                        "price": "120000", # قیمت پایه (مثلا متری ۱۲۰ هزار تومان)
                        "has_quantity": False, # کاربر تعداد/متراژ را وارد می‌کند
                        "price_per_unit": 1,
                        "is_active": True
                    },
                    "pricing_config": {
                        "base_setup_price": 50000, # هزینه حلقه و پانچ
                        "allow_custom_quantity": True,
                        "min_quantity": 1,
                        "max_quantity": 100,
                        "accepts_custom_dimensions": True, # کاربر طول و عرض وارد می‌کند
                        "min_width": 100,
                        "max_width": 300
                    },
                    "quantities": [], # خالی چون تیراژ ثابت ندارد
                    "sizes": []       # خالی چون سایز دلخواه است
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
        
        return Response({'id': product.id, 'message': 'اطلاعات پایه محصول با موفقیت ایجاد شدند.'}, status=status.HTTP_201_CREATED)

    # ========== UPDATE CORE ========== #
    @extend_schema(
        summary="ویرایش اطلاعات پایه محصول",
        request=ProductCoreCreateSerializer,
        examples=[
            OpenApiExample(
                'Update Example',
                summary='تغیر قیمت تیراژها و غیرفعال کردن محصول',
                value={
                    "shell": {
                        "is_active": False, # غیرفعال کردن موقت
                        "guide_text": "به علت نوسانات ارز، فروش متوقف است.",
                        "guide_type": "danger"
                    },
                    "quantities": [
                        {
                            "id": 10,
                            "guide_text": "قیمت جدید",
                            "guide_type": "warning"
                        }
                    ]
                },
                request_only=True,
            )
        ]
    )
    def update(self, request, id=None):
        """ ویرایش کلی اطلاعات پایه """
        serializer = ProductCoreCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        self.app_service.update_full_product_core(
            product_id=id, 
            user=request.user,
            data=serializer.validated_data
        )
        return Response({'status': 'Product core updated'})

    # ========== OPTIONS ========== #
    @extend_schema(
        summary="مرحله ۲: همگام‌سازی ویژگی‌ها (Options)",
        description="""
        **وظیفه:** اتصال ویژگی‌های محصول (رنگ، جنس، خدمات).
        
        **قابلیت‌های کلیدی:**
        1. **اتصال از بانک (Linked):** استفاده از `option_id` و `global_value_id`.
        2. **اورراید (Override):** تغییر نام/قیمت یک مقدار گلوبال فقط برای این محصول.
        3. **کاستوم (Custom):** افزودن یک مقدار کاملاً جدید که در بانک نیست (`global_value_id: null`).
        4. **راهنما (Guide):** افزودن راهنما برای کل گروه ویژگی یا تک‌تک مقادیر.
        """,
        request=ProductOptionsBulkSerializer,
        examples=[
            OpenApiExample(
                'Full Options Scenario',
                summary='سناریو کامل: ویژگی متصل (بانک) + ویژگی کاملاً اختصاصی',
                description="""
                در این مثال:
                1. ویژگی 'جنس کاغذ' (ID: 10) از بانک متصل می‌شود.
                2. یک ویژگی کاملاً جدید به نام 'بسته‌بندی ویژه' (بدون اتصال به بانک) ساخته می‌شود.
                """,
                value={
                    "options": [
                        # 1. ویژگی متصل به بانک (همراه با Override و Custom Value)
                        {
                            "option_id": 10, 
                            "is_required": True,
                            "guide_text": "انتخاب جنس کاغذ",
                            "values_config": [
                                { "global_value_id": 101, "price_impact": 0 }, # استفاده استاندارد
                                { "global_value_id": None, "label": "کاغذ خاص", "price_impact": 50000 } # مقدار کاستوم برای ویژگی بانک
                            ]
                        },
                        {
                            "option_id": None, # نال یعنی ویژگی جدید بساز
                            "name": "special_packaging",
                            "label": "نوع بسته‌بندی (اختصاصی)",
                            "input_type": "radio", # تعیین نوع ورودی
                            "is_required": False,
                            "guide_text": "فقط برای هدایای تبلیغاتی",
                            "guide_type": "tip",
                            "values_config": [
                                {
                                    "global_value_id": None, # همه مقادیرش باید کاستوم باشند
                                    "label": "جعبه چوبی",
                                    "value": "wood_box",
                                    "price_impact": 150000
                                },
                                {
                                    "global_value_id": None,
                                    "label": "کیسه پارچه‌ای",
                                    "value": "fabric_bag",
                                    "price_impact": 20000,
                                    "is_default": True
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
    
    # ========== UPDATE OPTION CONFIG ========== #
    @extend_schema(
        summary="ویرایش تنظیمات یک ویژگی خاص (تکی)",
        description="""
        اگر نخواهید همه آپشن‌ها را دوباره بفرستید و فقط بخواهید قیمت یا تنظیمات یکی را عوض کنید.
        """,
        request=OptionConfigUpdateSerializer,
        examples=[
            OpenApiExample(
                'Update Single Option',
                summary='تغییر قیمت گلاسه',
                value={
                    "product_option_id": 450,
                    "is_required": True,
                    "guide_text": "قیمت‌ها بروز شد",
                    "guide_type": "info",
                    "values": [
                        {
                            "id": 1200,
                            "price_impact": "8000",
                            "is_default": True
                        }
                    ]
                }
            )
        ]
    )
    @action(detail=True, methods=['patch'], url_path='update-option-config')
    def update_option_config(self, request, id=None):
        """ ویرایش تنظیمات ویژگی (تکی) """
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

    # ========== MEDIA SYNC ========== #
    @extend_schema(
        summary="مرحله ۳: اتصال فایل‌ها و تصاویر (Media)",
        request=ProductMediaSyncSerializer,
        examples=[
            OpenApiExample(
                'Media Sync Example',
                summary='مرتب‌سازی تصاویر و لینک فایل',
                value={
                    "attachment_ids_to_link": [15],
                    "attachment_ids_to_unlink": [],
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

    # ========== UPLOAD IMAGE ========== #
    @extend_schema(
        summary="آپلود تصویر (تکی)",
        request=ProductImageSerializer,
        description="تصویر را آپلود می‌کند و ID آن را برمی‌گرداند تا در `media-sync` استفاده شود."
    )
    @action(detail=True, methods=['post'], url_path='upload-image', parser_classes=[MultiPartParser, FormParser, JSONParser])
    def upload_image(self, request, id=None):
        """ آپلود عکس محصول """
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({'image': 'File required'}, status=status.HTTP_400_BAD_REQUEST)

        result = self.app_service.upload_product_image_async(
            product_id=id,
            user=request.user,
            file_obj=file_obj
        )
        
        if result['status'] == 'processing':
            return Response(result, status=status.HTTP_202_ACCEPTED)
        return Response(result, status=status.HTTP_201_CREATED)

    # ========== UPLOAD ATTACHMENT ========== #
    @extend_schema(
        summary="آپلود فایل در کتابخانه",
        request=AttachmentLibrarySerializer,
        description="فایل‌های جانبی (قالب، راهنما) را آپلود می‌کند."
    )
    @action(detail=False, methods=['post'], url_path='upload-attachment', parser_classes=[MultiPartParser, FormParser])
    def upload_attachment(self, request):
        """ آپلود فایل برای لینک کردن بعدی """
        file_obj = request.FILES.get('file')
        name = request.data.get('name')
        product_id = request.data.get('product_id')
        
        if not file_obj or not name:
            return Response({'detail': 'File and name are required.'}, status=status.HTTP_400_BAD_REQUEST)

        result = self.app_service.upload_attachment_library_async(
            user=request.user,
            file_obj=file_obj,
            product_id=product_id,
            name=name
        )
        
        if result['status'] == 'processing':
            return Response(result, status=status.HTTP_202_ACCEPTED)
        return Response(result, status=status.HTTP_201_CREATED)

    # ========== GET DETAIL ========== #
    @extend_schema(responses=ProductDetailSerializer)
    def retrieve(self, request, id=None):
        """ دریافت جزئیات کامل محصول """
        try:
            data = self.app_service.get_product_detail(id)
            serializer = ProductDetailSerializer(data, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ========== DELETE ========== #
    def destroy(self, request, id=None):
        """ حذف محصول """
        self.app_service.delete_product(id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ========== REMOVE OPTION ========== #
    @extend_schema(summary="حذف یک ویژگی از محصول")
    @action(detail=True, methods=['delete'], url_path='options/(?P<option_id>\d+)')
    def remove_option(self, request, id=None, option_id=None):
        """ حذف ویژگی از محصول """
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
        """ تغییر وضعیت گروهی """
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
        )
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
