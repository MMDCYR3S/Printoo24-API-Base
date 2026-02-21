from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes, inline_serializer, OpenApiResponse
from rest_framework import serializers

# ===== ایمپورت سرویس‌ها و سریالایزرها ===== #
from apps.dashboard.services import ProductDashboardService
from ..serializers import (
    ProductCoreCreateSerializer,
    ProductOptionsBulkSerializer,
    ProductMediaSyncSerializer,
    ProductDetailSerializer,
    OptionConfigUpdateSerializer,
    ProductSerializer,
    ProductQuantityOutputSerializer
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
                        "description": ".......",
                        "has_price": True,
                        "price": 20000,
                        "show_price": 100000,
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
                            "price": 120000,
                            "guide_text": "پرفروش‌ترین",
                            "guide_type": "tip"
                        },
                        {
                            "id": 11,
                            "price": 120000,
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
                            "price": 120000,
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
     # ========== OPTIONS ========== #
    @extend_schema(
        summary="مرحله ۲: همگام‌سازی ویژگی‌ها (Options)",
        description="""
        **وظیفه:** اتصال ویژگی‌های محصول (رنگ، جنس، خدمات).
        
        **خروجی:** لیستی از اشیاء شامل `product_option_id` (شناسه ذخیره شده در دیتابیس) و وضعیت همگام‌سازی.
        """,
        request=ProductOptionsBulkSerializer,
        responses={
            200: inline_serializer(
                name='BulkSyncOptionsResponse',
                fields={
                    'results': serializers.ListField(
                        child=inline_serializer(
                            name='SyncResultItem',
                            fields={
                                'product_option_id': serializers.IntegerField(help_text="شناسه یکتای ProductOption ایجاد شده در دیتابیس"),
                                'source_option_id': serializers.IntegerField(allow_null=True, help_text="شناسه ویژگی در بانک (اگر متصل باشد)"),
                                'status': serializers.CharField()
                            }
                        )
                    )
                }
            ),
            400: OpenApiResponse(description="خطای اعتبارسنجی (مثل نبودن label برای کاستوم)")
        },
        examples=[
            OpenApiExample(
                'Fully Custom Scenario with Multiple Conditions',
                summary='سناریو پیشرفته: کاملاً کاستوم + شناسه موقت (ref_id) + شروط چندگانه',
                description='در این مثال هیچ ویژگی‌ای در دیتابیس وجود ندارد. فرانت‌اند شناسه‌های موقت (ref_id) می‌سازد و شروط را بر اساس آن‌ها متصل می‌کند.',
                value={
                    "options": [
                        # ====== ویژگی سفارشی ۱: جنس اختصاصی ======
                        {
                            "option_id": None, 
                            "name": "custom_material",
                            "label": "جنس اختصاصی",
                            "input_type": "radio",
                            "is_required": True,
                            "values_config": [
                                {
                                    "ref_id": "mat_temp_1", # شناسه موقت ۱
                                    "global_value_id": None,
                                    "label": "مقوای ضخیم",
                                    "price_impact": 0
                                },
                                {
                                    "ref_id": "mat_temp_2", # شناسه موقت ۲
                                    "global_value_id": None,
                                    "label": "چوب وارداتی",
                                    "price_impact": 50000
                                }
                            ]
                        },
                        # ====== ویژگی سفارشی ۲: نوع برش ======
                        {
                            "option_id": None,
                            "name": "cut_type",
                            "label": "نوع برش",
                            "input_type": "select",
                            "is_required": False,
                            "values_config": [
                                {
                                    "ref_id": "cut_temp_1", # شناسه موقت ۳
                                    "global_value_id": None,
                                    "label": "برش لیزر دقیق",
                                    "price_impact": 20000
                                }
                            ]
                        },
                        # ====== ویژگی سفارشی ۳: با ماتریس قیمت و شروط چندگانه ======
                        {
                            "option_id": None,
                            "name": "special_packing",
                            "label": "بسته‌بندی ویژه",
                            "input_type": "checkbox",
                            "is_required": False,
                            "values_config": [
                                {
                                    "ref_id": "pack_temp_1",
                                    "global_value_id": None,
                                    "label": "باکس چوبی مگنت‌دار",
                                    "price_impact": 150000,
                                    "quantity_prices": [
                                        {"quantity_id": 10, "price": 300000},
                                        {"quantity_id": 11, "price": 500000},
                                        {"quantity_id": 12, "price": 800000}
                                    ],
                                    # شروط چندگانه با ارجاع به شناسه‌های موقت ویژگی‌های بالایی
                                    "conditions": [
                                        {
                                            "required_ref_id": "mat_temp_2", # باید چوب انتخاب شده باشد
                                            "action": "show"
                                        },
                                        {
                                            "required_ref_id": "cut_temp_1", # و همچنین باید برش لیزر باشد
                                            "action": "show"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                request_only=True
            ),
            OpenApiExample(
                'Unit-Based Product Scenario (No Quantity Matrix)',
                summary='سناریو محصول تعدادی (بدون ماتریس قیمت)',
                description='برای محصولاتی که تیراژ فرمی ندارند (مثل ماگ یا تیشرت). در اینجا آرایه quantity_prices خالی است و سیستم فقط از price_impact به عنوان قیمت پایه ضرب‌در تعداد استفاده می‌کند.',
                value={
                    "options": [
                        # ====== ویژگی ۱: رنگ محصول (از بانک) ======
                        {
                            "option_id": 20, # مثلا شناسه ویژگی 'رنگ ماگ'
                            "is_required": True,
                            "values_config": [
                                {
                                    "global_value_id": 301, # رنگ سفید
                                    "price_impact": 0, # بدون هزینه اضافه
                                    "quantity_prices": [], # <--- خالی (چون تیراژ نداریم)
                                    "conditions": []
                                },
                                {
                                    "global_value_id": 302, # رنگ طلایی
                                    "price_impact": 15000, # 15 هزار تومان به ازای هر دونه اضافه می‌شود
                                    "quantity_prices": [],
                                    "conditions": []
                                }
                            ]
                        },
                        # ====== ویژگی ۲: چاپ اختصاصی (کاستوم با شرط) ======
                        {
                            "option_id": None,
                            "name": "custom_print",
                            "label": "خدمات چاپ اختصاصی",
                            "input_type": "checkbox",
                            "is_required": False,
                            "values_config": [
                                {
                                    "ref_id": "print_temp_1",
                                    "global_value_id": None,
                                    "label": "چاپ طرح در هر دو طرف ماگ",
                                    "price_impact": 25000, # 25 هزار تومان اضافه به ازای هر عدد
                                    "quantity_prices": [],
                                    "conditions": [
                                        {
                                            # این گزینه فقط برای رنگ سفید فعال است
                                            "required_value_id": 301, 
                                            "action": "show"
                                        }
                                    ]
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
        
        try:
            results = self.app_service.bulk_sync_options(
                product_id=id, 
                options_data=serializer.validated_data['options']
            )
            return Response({'results': results}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"detail": str(e), "code": "sync_failed"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # ========== UPDATE OPTION CONFIG ========== #
    @extend_schema(
        summary="ویرایش تنظیمات یک ویژگی خاص (تکی) + ماتریس قیمت + وابستگی‌ها",
        description="""
        **معماری جدید:**
        شما در این اندپوینت می‌توانید برای هر مقدار، هم ماتریس قیمت تیراژ (`quantity_prices`)
        و هم لیست وابستگی‌ها (`conditions`) را ارسال کنید.
        """,
        request=OptionConfigUpdateSerializer,
        examples=[
            OpenApiExample(
                'Comprehensive Update Scenario',
                summary='سناریو فول ویرایش: آپدیت مقدار قدیمی + افزودن مقادیر جدید وابسته به هم (ref_id)',
                description='در این مثال پیچیده، یک مقدار قدیمی (id:1200) آپدیت می‌شود. دو مقدار جدید (بدون id) اضافه می‌شوند و یکی از این مقادیر جدید، وابسته به مقدار جدید دیگر است!',
                value={
                    "product_option_id": 450,
                    "is_required": True,
                    "values": [
                        # ====== آیتم اول: مقداری که از قبل در دیتابیس وجود دارد ======
                        {
                            "id": 1200, 
                            "price_impact": "0",
                            "is_default": False,
                            "quantity_prices": [
                                {"quantity_id": 1, "price": 50000},
                                {"quantity_id": 2, "price": 90000}
                            ],
                            "conditions": [
                                {
                                    "required_value_id": 50, # وابسته به یک آیتم قدیمیِ دیگر
                                    "action": "show"
                                }
                            ]
                        },
                        # ====== آیتم دوم: مقدار کاملا جدید (بدون وابستگی) ======
                        {
                            "id": None, 
                            "ref_id": "temp_mat_01", # شناسه موقت ۱
                            "label": "جنس چرم وارداتی",
                            "value": "leather_mat",
                            "price_impact": "25000",
                            "is_default": False,
                            "quantity_prices": [],
                            "conditions": []
                        },
                        # ====== آیتم سوم: مقدار کاملا جدید، وابسته به آیتم جدیدِ دوم! ======
                        {
                            "id": None, 
                            "ref_id": "temp_cover_01", # شناسه موقت ۲
                            "label": "روکش مخمل روی چرم",
                            "value": "velvet_cover",
                            "price_impact": "10000",
                            "is_default": False,
                            "quantity_prices": [],
                            "conditions": [
                                {
                                    # اینجا فرانت‌اند از شناسه موقتِ آیتم دوم استفاده می‌کند!
                                    "required_ref_id": "temp_mat_01", 
                                    "action": "show"
                                }
                            ]
                        }
                    ]
                },
                request_only=True
            ),
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
        summary="نکته مهم: این قسمت بعد از اعمال تغییرات حذف میشه.",
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
        summary="مرحله 3: آپلود عکس",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'فایل تصویر محصول (JPG, PNG, etc.)'
                    }
                },
                'required': ['image']
            }
        },
        responses={
            202: OpenApiResponse(
                description="تصویر در حال پردازش است",
                examples=[
                    OpenApiExample(
                        name="Processing Response",
                        value={
                            "status": "processing",
                            "task_id": "550e8400-e29b-41d4-a716-446655440000"
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="خطا در درخواست",
                examples=[
                    OpenApiExample(
                        name="Error Response",
                        value={
                            "image": "File required"
                        }
                    )
                ]
            )
        },
        description="""
        
        مثال:
        {
            "image": "product_01.png" // فایل آپلود شده از Input
            "order": 2
        }



        



        *** اگر از موارد بالا نتیجه نگرفتی و مثال بهت کمک نکرد، از فرمت زیر کمک بگیر. شاید بهت کمک کرد. این فرمت رو میتونی به AI بدی و ازش راهنمایی بخوای. ***
            ```
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'فایل تصویر محصول (JPG, PNG, etc.)'
                    }
                },
                'required': ['image']
            }
            ```
        """
    )
    @action(detail=True, methods=['post'], url_path='upload-image', parser_classes=[MultiPartParser, FormParser, JSONParser])
    def upload_image(self, request, id=None):
        """ آپلود عکس محصول """
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({'image': 'File required'}, status=status.HTTP_400_BAD_REQUEST)

        order = request.data.get('order', 0)
        try:
            order = int(order)
        except (ValueError, TypeError):
            order = 0

        result = self.app_service.upload_product_image_async(
            product_id=id,
            user=request.user,
            file_obj=file_obj,
            order=order
        )
        
        if result['status'] == 'processing':
            return Response(result, status=status.HTTP_202_ACCEPTED)
        return Response(result, status=status.HTTP_201_CREATED)

    # ========== UPLOAD ATTACHMENT ========== #
    @extend_schema(
        summary="مرحله 4: آپلود فایل‌های پیوست",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'فایل پیوست (PDF, DOC, etc.)'
                    },
                    'name': {
                        'type': 'string',
                        'description': 'نام فایل (اختیاری)',
                        'nullable': True
                    },
                    'product_id': {
                        'type': 'integer',
                        'description': 'شناسه محصول'
                    }
                },
                'required': ['file', 'product_id']
            }
        },
        responses={
            201: OpenApiResponse(
                description="فایل با موفقیت آپلود شد",
                examples=[
                    OpenApiExample(
                        name="Success Response",
                        value={
                            "id": 456,
                            "status": "created",
                            "file_url": "https://example.com/media/attachments/file.pdf",
                            "name": "دفترچه راهنما",
                            "product_id": 5
                        }
                    )
                ]
            ),
            202: OpenApiResponse(
                description="فایل در حال پردازش است",
                examples=[
                    OpenApiExample(
                        name="Processing Response",
                        value={
                            "status": "processing",
                            "task_id": "550e8400-e29b-41d4-a716-446655440001"
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="خطا در درخواست",
                examples=[
                    OpenApiExample(
                        name="Error Response",
                        value={
                            "detail": "File and product_id are required."
                        }
                    )
                ]
            )
        },
        description="""
        آپلود فایل‌های پیوست برای محصول.
        
        مثال:
        {
            "name": "فایل راهنما",
            "file": "document.pdf", // این قسمت همون فایل آپلود شده قرار میگیره
            "product_id": 5
        }




        **نکته:** نام می‌تواند خالی باشد و اجباری نیست.
        
        **نحوه استفاده در فرانت‌اند:**
            ```javascript
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                formData.append('name', 'دفترچه راهنما');  // اختیاری
                formData.append('product_id', 5);
                
                fetch('/api/products/upload-attachment/', {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer YOUR_TOKEN'
                    },
                    body: formData
                })
                .then(response => response.json())
                .then(data => console.log(data));
            ```

            




            ***اگر باز هم با وجود مثال بالا نتونستی کاری انجام بدی، می‌تونی این فرمت رو به AI بدی. این میتونه بهش کمک کنه که درک کنه دقیقا این API چیکار میکنه:***

            ```
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'فایل پیوست (PDF, DOC, etc.)'
                    },
                    'name': {
                        'type': 'string',
                        'description': 'نام فایل (اختیاری)',
                        'nullable': True
                    },
                    'product_id': {
                        'type': 'integer',
                        'description': 'شناسه محصول'
                    }
                },
                'required': ['file', 'product_id']
            }
            ```
        """
    )
    @action(detail=False, methods=['post'], url_path='upload-attachment', parser_classes=[MultiPartParser, FormParser])
    def upload_attachment(self, request):
        """ آپلود فایل برای لینک کردن بعدی """
        file_obj = request.FILES.get('file')
        name = request.data.get('name', '')
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

    @action(detail=True, methods=['get'], url_path='quantities')
    def get_quantities(self, request, id=None):
        """ لیست تیراژهای اختصاصی محصول """
        try:
            # فراخوانی سرویس اصلاح شده
            quantities = self.app_service.get_product_quantities(product_id=id)
            serializer = ProductQuantityOutputSerializer(quantities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
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
