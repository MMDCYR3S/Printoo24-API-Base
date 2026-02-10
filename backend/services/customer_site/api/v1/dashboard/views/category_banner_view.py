import re

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


from core.product.services import ProductCategoryService
from apps.shop.services import ShopCategoryService
from ..serializers.general_serializers import (
    ProductCategoryDashboardSerializer,
    ParentCategoryListSerializer,
    ProductCategoryDetailWithLinksSerializer,
    SubcategoryWithParentSerializer,
    CategoryBulkUpsertSerializer,
)

# ===== ویو‌ست مدیریت دسته‌بندی‌ها ===== #
@extend_schema(tags=['Dashboard-Category-Banner'])
class ProductCategoryDashboardViewSet(ModelViewSet):
    """
    این ویو‌ست تمامی عملیات CRUD برای دسته‌بندی‌ها را مدیریت می‌کند.
    شامل: لیست، جزئیات، افزودن، ویرایش، حذف و عملیات گروهی.
    """
    serializer_class = ProductCategoryDashboardSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    
    # ===== تزریق وابستگی ===== #
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProductCategoryService()

    # ===== بازنویسی متد get_queryset ===== #
    def get_queryset(self):
        return self.service.get_category_tree_queryset()
     
    # ===== بازنویسی متد retrieve (مشاهده جزئیات) ===== #
    @extend_schema(
        summary="مشاهده جزئیات دسته‌بندی",
        description="نمایش جزئیات کامل. اگر دسته‌بندی دارای فرزند باشد، لینک آن‌ها نمایش داده می‌شود.",
        responses=ProductCategoryDetailWithLinksSerializer
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProductCategoryDetailWithLinksSerializer(instance, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        summary="لیست دسته‌بندی‌های والد (ریشه)",
        description="نمایش فقط دسته‌بندی‌های سطح بالا بدون عکس، همراه با لینک دسترسی به جزئیات.",
        responses=ParentCategoryListSerializer(many=True)
    )
    def list(self, request):
        """
        اکشن اختصاصی برای گرفتن لیست والدها
        """
        queryset = self.service.get_root_categories()
        
        serializer = ParentCategoryListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    # ===== بازنویسی متد create (افزودن) ===== #
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # پاس دادن داده‌های معتبر به سرویس دامین
        instance = self.service.create_category(serializer.validated_data)
        
        # سریالایز کردن مجدد برای پاسخ
        output_serializer = self.get_serializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    # ===== بازنویسی متد update (ویرایش) ===== #
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_instance = self.service.update_category(instance, serializer.validated_data)
        
        output_serializer = self.get_serializer(updated_instance)
        return Response(output_serializer.data)

    # ===== بازنویسی متد destroy (حذف) ===== #
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.delete_category(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="لیست تمام زیردسته‌بندی‌ها",
        description="لیست تمام زیردسته‌ها به صورت مسطح به همراه نام و اطلاعات والدین آن‌ها. مناسب برای فیلترها.",
        responses=SubcategoryWithParentSerializer(many=True)
    )
    @action(detail=False, methods=['get'], url_path='subcategories')
    def sub_categories(self, request, *args, **kwargs):
        service = ShopCategoryService(request=request)
        categories_data = service.get_subcategories_flat_list()
        return Response(categories_data)

    # ===== اکشن سفارشی: ایجاد و ویرایش گروهی ===== #
    @extend_schema(
        request=CategoryBulkUpsertSerializer(many=True),
        summary="ایجاد و ویرایش گروهی دسته‌بندی‌ها",
        description="این اکشن امکان ثبت همزمان چندین دسته‌بندی را فراهم می‌کند. " \
                    "با ارسال id، آیتم ویرایش می‌شود. عدم ارسال id باعث ایجاد جدید می‌شود. " \
                    "برای اتصال فرزند به والد می‌توانید از parent_slug استفاده کنید. " \
                    "نکته: برای ارسال عکس، درخواست باید به صورت multipart/form-data باشد.",
        examples=[
            OpenApiExample(
                "Bulk Insert with Images",
                summary="ایجاد دسته‌ها با عکس",
                description="نمونه ایجاد دسته‌بندی جدید به همراه آپلود بنرها.",
                value=[
                    {
                        "name": "الکترونیک",
                        "description": "تجهیزات دیجیتال و الکترونیکی",
                        "banner_wide": "(Binary File)",
                        "banner_box": "(Binary File)",
                        "is_active": True
                    },
                    {
                        "name": "گوشی موبایل",
                        "parent_slug": "electronics",
                        "banner_box": "(Binary File)",
                        "is_active": True
                    }
                ]
            ),
            OpenApiExample(
                "Bulk Upsert (Mix)",
                summary="ترکیب ویرایش و ایجاد",
                description="مثال ترکیبی: آیتم اول ویرایش می‌شود (چون ID دارد) و عکسش تغییر می‌کند. آیتم دوم جدید ایجاد می‌شود.",
                value=[
                    {
                        "id": 45,
                        "name": "لپ تاپ (ویرایش شده)",
                        "parent_slug": "electronics", 
                        "banner_wide": "(Binary File - New Banner)",
                        "is_active": True
                    },
                    {
                        "name": "لوازم جانبی لپ‌تاپ",
                        "parent_slug": "electronics",
                        "description": "کیف، موس و خنک کننده",
                        "banner_box": "(Binary File)",
                        "is_active": True
                    }
                ]
            )
        ],
        responses={200: list}
    )
    @action(detail=False, methods=['post'], url_path='bulk-upsert')
    def bulk_upsert(self, request):
        # ===== درخواست خام ===== #
        raw_data = request.data
        
        # ===== اگر درخواست مولتی بود ===== #
        if 'multipart/form-data' in request.content_type:
            formatted_data = self._transform_multipart_data(request)
        else:
            formatted_data = request.data
        
        # ===== اعتبارسنجی ===== #
        serializer = CategoryBulkUpsertSerializer(data=formatted_data, many=True)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        
        # ===== ارسال به سرویس ===== #
        result = self.service.bulk_upsert_categories(validated_data, request.user)
        
        return Response(
            {
                "detail": "عملیات گروهی با موفقیت انجام شد.",
                "results": result
            },
            status=status.HTTP_200_OK
        )
    # ===== اکشن سفارشی: تغییر وضعیت گروهی ===== #
    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(name='ids', type=list, location=OpenApiParameter.QUERY, description='لیست شناسه ها'),
            OpenApiParameter(name='active', type=bool, location=OpenApiParameter.QUERY, description='وضعیت جدید')
        ],
        summary="تغییر وضعیت گروهی"
    )
    @action(detail=False, methods=['patch'], url_path='bulk-status')
    def bulk_status(self, request):
        ids = request.data.get('ids', [])
        is_active = request.data.get('is_active', True)
        
        if not ids:
            return Response({'detail': 'لیست شناسه (ids) الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)
            
        count = self.service.bulk_toggle_status(ids, is_active)
        return Response({'detail': f'{count} دسته‌بندی بروزرسانی شدند.'}, status=status.HTTP_200_OK)

    # ===== اکشن سفارشی: حذف گروهی ===== #
    @extend_schema(summary="حذف گروهی")
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
             return Response({'detail': 'لیست شناسه (ids) الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)
        
        self.service.bulk_delete(ids)
        return Response({'detail': 'موارد انتخاب شده حذف شدند.'}, status=status.HTTP_204_NO_CONTENT)

    def _transform_multipart_data(self, request) -> list:
        """
        تبدیل هوشمند داده‌های Multipart به لیست.
        تغییر: جدا کردن پردازش POST و FILES برای تضمین دریافت عکس‌ها.
        """
        items_dict = {}

        def parse_key_value(key, value):
            match = re.search(r'\[(\d+)\]\.?(\w+)', key)
            if match:
                index = int(match.group(1))
                field_name = match.group(2)
                
                if index not in items_dict:
                    items_dict[index] = {}
                
                items_dict[index][field_name] = value
            elif key in ['id', 'name', 'slug', 'parent_slug', 'description', 'is_active', 'banner_wide', 'banner_box']:
                if 0 not in items_dict: items_dict[0] = {}
                items_dict[0][key] = value

        if hasattr(request, 'POST'):
            for key, value in request.POST.items():
                parse_key_value(key, value)
        
        if hasattr(request, 'FILES'):
            for key, value in request.FILES.items():
                parse_key_value(key, value)

        return [items_dict[i] for i in sorted(items_dict.keys())]
