from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import (
    extend_schema, OpenApiExample, OpenApiTypes, 
    inline_serializer, OpenApiResponse, OpenApiParameter
)
from rest_framework import serializers

from apps.dashboard.services import ProductDashboardService
from ..serializers import (
    ProductSerializer, ProductShellSerializer,
    ProductCoreCreateSerializer, ProductDetailSerializer,
    ProductFieldsBulkSyncSerializer, ProductFormulasBulkSyncSerializer,
)


@extend_schema(tags=['Dashboard-Product'])
class ProductDashboardViewSet(viewsets.ViewSet):
    """
    مدیریت جامع محصولات در ۳ مرحله:
    1. ایجاد/ویرایش هسته محصول (Core)
    2. همگام‌سازی فیلدها و شرط‌ها (Form Builder)
    3. همگام‌سازی فرمول‌های قیمت‌گذاری (Formula Builder)
    4. آپلود رسانه
    """
    lookup_field = 'id'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_service = ProductDashboardService()

    # ========== LIST ========== #
    @extend_schema(summary="لیست محصولات", responses=ProductSerializer(many=True))
    def list(self, request):
        try:
            products = self.app_service.get_all_products()
            serializer = ProductSerializer(products, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ========== CREATE ========== #
    @extend_schema(
        summary="مرحله ۱: ایجاد هسته محصول",
        description="""
        ایجاد ساختار اولیه محصول.
        در این مرحله یک `category_id` (دسته اصلی) و یک `subcategory_id` (زیردسته) ارسال می‌شود.
        """,
        request=ProductCoreCreateSerializer,
        responses={201: inline_serializer('CreateResponse', fields={
            'id': serializers.IntegerField(),
            'message': serializers.CharField(),
        })},
        examples=[
            OpenApiExample(
                name='ایجاد محصول ساده',
                summary='ارسال مشخصات به همراه دسته والد و فرزند',
                value={
                    "shell": {
                        "name": "کارت ویزیت لمینت براق",
                        "category_id": 5,             # <--- شناسه دسته اصلی
                        "subcategory_id": 12,         # <--- شناسه زیردسته
                        "description": "چاپ افست با کیفیت بالا",
                        "has_price": True,
                        "price": "20000.00",
                        "show_price": "100000.00",
                        "price_per_unit": 1000,
                        "has_quantity": True,
                        "is_active": True,
                        "guide_text": "زمان تحویل ۷ روز کاری است.",
                        "guide_type": "info"
                    }
                },
                request_only=True,
            )
        ]
    )
    def create(self, request):
        serializer = ProductCoreCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = self.app_service.create_product_core(
            user=request.user,
            data=serializer.validated_data['shell']
        )
        return Response(
            {'id': product.id, 'message': 'محصول با موفقیت ایجاد شد.'},
            status=status.HTTP_201_CREATED
        )

    # ========== UPDATE ========== #
    @extend_schema(
        summary="ویرایش اطلاعات پایه (هسته) محصول",
        description="""
        شما می‌توانید کل فیلدها یا فقط فیلدهایی که تغییر کرده‌اند را ارسال کنید (Partial Update).
        اگر قصد تغییر دسته‌بندی را دارید، باید `category_id` و `subcategory_id` را ارسال کنید.
        """,
        request=ProductCoreCreateSerializer,
        responses={200: inline_serializer('UpdateResponse', fields={
            'message': serializers.CharField(),
        })},
        examples=[
            OpenApiExample(
                name='۱. ویرایش کامل (Full Update)',
                summary='تغییر کامل هسته از جمله دسته‌بندی‌ها',
                description='تمامی فیلدها ارسال شده و مقادیر جایگزین می‌شوند.',
                value={
                    "shell": {
                        "name": "کارت ویزیت لمینت براق (ویرایش شده)",
                        "category_id": 8,             # <--- تغییر دسته اصلی
                        "subcategory_id": 15,         # <--- تغییر زیردسته
                        "description": "توضیحات جدید محصول",
                        "has_price": True,
                        "price": "25000.00",
                        "show_price": "120000.00",
                        "price_per_unit": 1000,
                        "has_quantity": True,
                        "is_active": True,
                        "guide_text": "زمان تحویل به ۱۰ روز کاری تغییر یافت.",
                        "guide_type": "warning"
                    }
                },
                request_only=True,
            ),
            OpenApiExample(
                name='۲. ویرایش جزئی (Partial Update)',
                summary='فقط غیرفعال کردن محصول و تغییر پیام',
                description='در این حالت بقیه اطلاعات از جمله دسته‌بندی‌ها در دیتابیس دست‌نخورده باقی می‌مانند.',
                value={
                    "shell": {
                        "is_active": False,
                        "guide_text": "فروش این محصول موقتاً متوقف شده است.",
                        "guide_type": "warning"
                    }
                },
                request_only=True,
            )
        ]
    )
    def update(self, request, id=None):
        serializer = ProductCoreCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        self.app_service.update_product_core(
            product_id=id,
            user=request.user,
            data=serializer.validated_data.get('shell', {})
        )
        return Response({'message': 'محصول با موفقیت ویرایش شد.'}, status=status.HTTP_200_OK)

    # ========== RETRIEVE ========== #
    @extend_schema(summary="جزئیات کامل محصول", responses=ProductDetailSerializer)
    def retrieve(self, request, id=None):
        try:
            data = self.app_service.get_product_detail(id)
            product = data['product']
            serializer = ProductDetailSerializer(product, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ========== DELETE ========== #
    @extend_schema(summary="حذف محصول")
    def destroy(self, request, id=None):
        self.app_service.delete_product(id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ========== SYNC FIELDS ========== #
    @extend_schema(
        summary="مرحله ۲: همگام‌سازی فیلدها و شرط‌ها",
        description="""
        ارسال کل ساختار فرم (فیلدها، گزینه‌ها، شرط‌های وابستگی) در یک درخواست.
        
        **📌 مقادیر مجاز (Enums) که فرانت‌اند باید رعایت کند:**
        
        **۱. انواع فیلد (`field_type`):**
        - `text` : متن کوتاه
        - `textarea` : متن چندخطی
        - `number` : عدد
        - `single_select` : تک انتخابی (Radio)
        - `multi_select` : چند انتخابی (Checkbox)
        - `dropdown` : کشویی (Select)

        **۲. عملگر داخلی چندانتخابی (`multi_select_operator`):**
        *(فقط زمانی کاربرد دارد که نوع فیلد multi_select یا checkbox باشد)*
        - `add` : جمع (+)
        - `sub` : تفریق (-)
        - `mul` : ضرب (*)
        - `div` : تقسیم (/)

        **۳. عملگر شرط (`operator`):**
        - `equals` : برابر با
        - `not_equals` : به غیر از
        - `is_empty` : خالی باشد
        - `is_not_empty` : خالی نباشد

        **۴. عملیات شرط (`action`):**
        - `show` : آشکار شود
        - `hide` : پنهان شود
        - `enable` : فعال شود
        - `disable` : غیرفعال شود
        """,
        request=ProductFieldsBulkSyncSerializer,
        responses={200: inline_serializer('SyncFieldsResponse', fields={
            'message': serializers.CharField(),
        })},
        examples=[
            OpenApiExample(
                '1. Create Scenario',
                summary='سناریو ایجاد: ساخت فیلدهای جدید (فقط با temp_id)',
                value={
                    "fields": [
                        {
                            "temp_id": "field_new_1",
                            "title": "نوع کاغذ",
                            "field_type": "dropdown",
                            "is_required": True,
                            "order": 1,
                            "choices": [
                                {"temp_id": "choice_new_1", "title": "گلاسه ۱۳۵", "numeric_value": "0.00", "order": 1, "is_default": True}, # 👈 اضافه شدن is_default
                                {"temp_id": "choice_new_2", "title": "گلاسه ۱۷۰", "numeric_value": "5000.00", "order": 2, "is_default": False} # 👈 اضافه شدن is_default
                            ],
                            "conditions": []
                        },
                        {
                            "temp_id": "field_new_2",
                            "title": "تعداد رنگ",
                            "field_type": "single_select",
                            "is_required": True,
                            "order": 2,
                            "choices": [
                                {"temp_id": "choice_new_3", "title": "۴ رنگ", "numeric_value": "0.00", "order": 1, "is_default": True}
                            ],
                            "conditions": [
                                {
                                    "trigger_field_id": "field_new_1",
                                    "operator": "equals",
                                    "trigger_choice_id": "choice_new_1",
                                    "action": "show"
                                }
                            ]
                        }
                    ]
                },
                request_only=True,
            ),
            OpenApiExample(
                '2. Update & Delete Scenario',
                summary='سناریو ویرایش و حذف: استفاده از ID دیتابیس',
                description='''
                در این مثال فرض می‌کنیم فیلدها قبلاً ساخته شده‌اند و ID دارند.
                ... (توضیحات قبلی) ...
                ''',
                value={
                    "fields": [
                        {
                            "id": 50, 
                            "title": "نوع کاغذ (ویرایش شده)",
                            "field_type": "dropdown",
                            "is_required": False, 
                            "order": 1,
                            "choices": [
                                {
                                    "id": 100, 
                                    "title": "گلاسه ۱۳۵", 
                                    "numeric_value": "2000.00", 
                                    "order": 1,
                                    "is_default": False # 👈 تغییر پیش‌فرض از سمت فرانت‌اند
                                },
                                {
                                    "temp_id": "choice_new_99", 
                                    "title": "کتان ۲۵۰", 
                                    "numeric_value": "15000.00", 
                                    "order": 3,
                                    "is_default": True # 👈 گزینه جدید حالا پیش‌فرض است
                                }
                            ],
                            "conditions": []
                        }
                    ]
                },
                request_only=True,
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='sync-fields')
    def sync_fields(self, request, id=None):
        serializer = ProductFieldsBulkSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.app_service.sync_product_fields(
                product_id=id,
                fields_data=serializer.validated_data['fields']
            )
            return Response({'message': 'فیلدهای محصول با موفقیت سینک شدند.'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== SYNC FORMULAS ========== #
    @extend_schema(
        summary="مرحله ۳: همگام‌سازی فرمول‌های قیمت‌گذاری",
        description="""
        **معماری فرمول‌ساز:**
        در این بخش شما با استفاده از شناسه (`id`) فیلدهایی که در مرحله قبل ساخته‌اید، فرمول ریاضی محصول را تعریف می‌کنید.
        
        **متغیرهای مجاز:**
        - `field_{id}`: ارجاع به هر فیلد داینامیک محصول (مثال: `field_12`)
        - `price_per_unit`: ارجاع به گام شمارش / تیراژ مبنای خود محصول
        - `base_price`: ارجاع به قیمت پایه خود محصول
        
        **مثال کاربردی:**
        فرمول: `((field_12 * field_15) + price_per_unit) + base_price`
        """,
        request=ProductFormulasBulkSyncSerializer,
        responses={200: inline_serializer('SyncFormulasResponse', fields={
            'message': serializers.CharField(),
        })},
        examples=[
            OpenApiExample(
                '1. Simple Formula Scenario',
                summary='سناریو ۱: یک فرمول ساده و پایه‌ای',
                description='وقتی محصول پیچیدگی خاصی ندارد و همیشه با یک فرمول خطی محاسبه می‌شود.',
                value={
                    "formulas": [
                        {
                            "title": "فرمول محاسبه قیمت استاندارد",
                            "condition_expression": None,
                            "calculation_expression": "(field_10 * field_12) + field_15"
                        }
                    ]
                },
                request_only=True,
            ),
            OpenApiExample(
                '2. Advanced Conditional Scenario',
                summary='سناریو ۲: قیمت‌گذاری پلکانی با فرمول‌های شرطی',
                description='وقتی فرمول محاسبه قیمت بر اساس تیراژ تغییر می‌کند. (مثلاً اگر تیراژ کمتر از ۱۰۰۰ بود فرمول ۱، و اگر بیشتر از ۱۰۰۰ بود فرمول ۲ با تخفیف اجرا شود).',
                value={
                    "formulas": [
                        {
                            "id": 1, # این فرمول قبلاً ساخته شده و حالا آپدیت می‌شود
                            "title": "قیمت برای تیراژ زیر ۱۰۰۰ (خرده فروشی)",
                            "condition_expression": "field_15 < 1000",
                            "calculation_expression": "(field_10 * field_12) * 1.5" # ضریب سود بیشتر
                        },
                        {
                            "id": 2, # این فرمول هم از قبل وجود داشته
                            "title": "قیمت برای تیراژ بالای ۱۰۰۰ (عمده)",
                            "condition_expression": "field_15 >= 1000",
                            "calculation_expression": "(field_10 * field_12) * 1.1" # ضریب تخفیف خورده
                        },
                        {
                            # فرمول جدید برای همکاران
                            "title": "فرمول اختصاصی مشتری همکار",
                            "condition_expression": "field_8 == 50", # مثلاً اگر فیلد نقش کاربر برابر با مقدار همکار بود
                            "calculation_expression": "(field_10 * field_12) + 5000"
                        }
                    ]
                },
                request_only=True,
            ),
            OpenApiExample(
                '3. Delete Orphan Formulas',
                summary='سناریو ۳: حذف فرمول‌ها',
                description='اگر می‌خواهید فرمول‌های قبلی محصول را پاک کنید و فقط یک فرمول جدید تنظیم کنید، کافیست فقط همان فرمول جدید را ارسال کنید. سیستم خودکار بقیه را پاک می‌کند.',
                value={
                    "formulas": [
                        {
                            "title": "فرمول جدید جایگزین بقیه",
                            "condition_expression": None,
                            "calculation_expression": "field_10 * field_20 * field_30"
                        }
                    ]
                },
                request_only=True,
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='sync-formulas')
    def sync_formulas(self, request, id=None):
        serializer = ProductFormulasBulkSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.app_service.sync_product_formulas(
                product_id=id,
                formulas_data=serializer.validated_data['formulas']
            )
            return Response({'message': 'فرمول‌های محصول با موفقیت اعمال شدند.'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== UPLOAD IMAGE ========== #
    @extend_schema(
        summary="آپلود تصویر محصول",
        request={'multipart/form-data': {
            'type': 'object',
            'properties': {
                'image': {'type': 'string', 'format': 'binary'},
                'order': {'type': 'integer', 'default': 0}
            },
            'required': ['image']
        }},
        responses={
            201: inline_serializer('ImageUploadedResponse', fields={
                'status': serializers.CharField(),
                'id': serializers.IntegerField(),
            }),
            202: inline_serializer('ImageQueuedResponse', fields={
                'status': serializers.CharField(),
                'detail': serializers.CharField(),
            }),
        }
    )
    @action(detail=True, methods=['post'], url_path='upload-image',
            parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, id=None):
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({'image': 'فایل تصویر الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = int(request.data.get('order', 0))
        except (ValueError, TypeError):
            order = 0

        result = self.app_service.upload_product_image_async(
            product_id=id, user=request.user, file_obj=file_obj, order=order
        )
        http_status = status.HTTP_202_ACCEPTED if result['status'] == 'processing' else status.HTTP_201_CREATED
        return Response(result, status=http_status)

    # ========== DELETE PRODUCT IMAGE ========== #
    @extend_schema(
        summary="حذف یک تصویر خاص از محصول",
        description="این اکشن تصویر مشخصی را با شناسه image_id از محصول مشخص شده با id حذف فیزیکی می‌کند.",
        parameters=[
            OpenApiParameter(name="id", type=int, location=OpenApiParameter.PATH, description="شناسه محصول"),
            OpenApiParameter(name="image_id", type=int, location=OpenApiParameter.PATH, description="شناسه تصویر")
        ]
    )
    @action(detail=True, methods=['delete'], url_path='delete-image/(?P<image_id>[0-9]+)')
    def delete_image(self, request, id=None, image_id=None):
        """
        حذف فیزیکی یک تصویر مشخص متصل به محصول از طریق App Service
        """
        try:
            self.app_service.delete_product_image_from_app(product_id=id, image_id=image_id)
            return Response({'message': 'تصویر محصول با موفقیت حذف شد.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== UPLOAD ATTACHMENT ========== #
    @extend_schema(
        summary="آپلود فایل پیوست",
        request={'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {'type': 'string', 'format': 'binary'},
                'name': {'type': 'string', 'nullable': True},
                'product_id': {'type': 'integer'}
            },
            'required': ['file', 'product_id']
        }},
        responses={
            201: inline_serializer('AttachmentCreatedResponse', fields={
                'status': serializers.CharField(),
                'id': serializers.IntegerField(),
            }),
            202: inline_serializer('AttachmentQueuedResponse', fields={
                'status': serializers.CharField(),
                'detail': serializers.CharField(),
            }),
        }
    )
    @action(detail=False, methods=['post'], url_path='upload-attachment',
            parser_classes=[MultiPartParser, FormParser])
    def upload_attachment(self, request):
        file_obj = request.FILES.get('file')
        product_id = request.data.get('product_id')

        if not file_obj or not product_id:
            return Response(
                {'detail': 'فایل و product_id الزامی هستند.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        name = request.data.get('name', '')
        result = self.app_service.upload_attachment_library_async(
            user=request.user, file_obj=file_obj, product_id=product_id, name=name
        )
        http_status = status.HTTP_202_ACCEPTED if result['status'] == 'processing' else status.HTTP_201_CREATED
        return Response(result, status=http_status)

    # ========== DELETE PRODUCT ATTACHMENT ========== #
    @extend_schema(
        summary="حذف یک فایل پیوست خاص از محصول",
        description="این اکشن فایل پیوست مشخصی را با شناسه attachment_id از محصول مشخص شده با id حذف فیزیکی می‌کند.",
        parameters=[
            OpenApiParameter(name="id", type=int, location=OpenApiParameter.PATH, description="شناسه محصول"),
            OpenApiParameter(name="attachment_id", type=int, location=OpenApiParameter.PATH, description="شناسه فایل پیوست")
        ]
    )
    @action(detail=True, methods=['delete'], url_path='delete-attachment/(?P<attachment_id>[0-9]+)')
    def delete_attachment(self, request, id=None, attachment_id=None):
        """
        حذف فیزیکی یک فایل پیوست مشخص متصل به محصول از طریق App Service
        """
        try:
            self.app_service.delete_product_attachment_from_app(product_id=id, attachment_id=attachment_id)
            return Response({'message': 'فایل پیوست با موفقیت حذف شد.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== BULK STATUS ========== #
    @extend_schema(
        summary="تغییر وضعیت گروهی",
        request=inline_serializer('BulkStatusUpdate', fields={
            'product_ids': serializers.ListField(child=serializers.IntegerField()),
            'is_active': serializers.BooleanField(),
        }),
        examples=[
            OpenApiExample(
                'فعال‌سازی گروهی',
                value={'product_ids': [10, 12, 15], 'is_active': True},
                request_only=True,
            )
        ]
    )
    @action(detail=False, methods=['patch'], url_path='bulk-status')
    def bulk_update_status(self, request):
        product_ids = request.data.get('product_ids', [])
        is_active = request.data.get('is_active')

        if not product_ids or is_active is None:
            return Response(
                {'error': 'product_ids و is_active الزامی هستند.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            count = self.app_service.bulk_update_product_status(product_ids, is_active)
            return Response({'message': f'{count} محصول بروزرسانی شد.', 'updated_count': count})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== BULK DELETE ========== #
    @extend_schema(
        summary="حذف گروهی",
        request=inline_serializer('BulkDelete', fields={
            'product_ids': serializers.ListField(child=serializers.IntegerField()),
        }),
        examples=[
            OpenApiExample(
                'حذف گروهی',
                value={'product_ids': [10, 12, 15]},
                request_only=True,
            )
        ]
    )
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        data = request.data
        product_ids = data if isinstance(data, list) else data.get('product_ids', [])

        if not product_ids:
            return Response({'error': 'product_ids الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = self.app_service.bulk_delete_products(product_ids)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)