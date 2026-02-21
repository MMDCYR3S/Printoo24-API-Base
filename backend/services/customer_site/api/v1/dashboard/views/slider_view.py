from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample

from apps.home.services import SliderService
from ..serializers import SliderDashboardSerializer

# ===== تنظیم Schema برای متدهایی که به صورت پیش‌فرض در ViewSet هستند (مثل list و retrieve) ===== #
@extend_schema_view(
    list=extend_schema(
        summary="دریافت لیست اسلایدرها",
        description="لیست تمامی اسلایدرهای صفحه اصلی را برمی‌گرداند.",
        examples=[
            OpenApiExample(
                name="مثال خروجی لیست",
                value=[{
                    "id": 1,
                    "name": "تخفیف یلدا",
                    "image_url": "http://api.printoo24.com/media/slider/yalda.jpg",
                    "link": "https://printoo24.com/yalda",
                    "created_at": "2023-11-20T10:00:00Z",
                    "updated_at": "2023-11-20T10:00:00Z"
                }],
                response_only=True,
            )
        ]
    ),
    retrieve=extend_schema(
        summary="دریافت جزئیات یک اسلایدر",
        description="با ارسال ID اسلایدر، اطلاعات دقیق آن را دریافت کنید."
    ),
    partial_update=extend_schema(
        summary="ویرایش جزئی اسلایدر (PATCH)",
        description="برای تغییر دادن فقط یک یا چند فیلد (مثلاً فقط تغییر لینک بدون ارسال مجدد عکس) استفاده می‌شود. دیتا باید FormData باشد."
    )
)
@extend_schema(tags=['Dashboard-Slider'])
class SliderDashboardViewSet(viewsets.ModelViewSet):
    """
    مدیریت اسلایدرهای صفحه اصلی (CRUD کامل).
    """
    serializer_class = SliderDashboardSerializer
    # این خط به Swagger می‌فهماند که ورودی باید از نوع multipart/form-data باشد
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SliderService()

    def get_queryset(self):
        return self.service.get_all()

    # ==========================================
    # ایجاد اسلایدر (POST)
    # ==========================================
    @extend_schema(
        summary="ایجاد اسلایدر جدید (POST)",
        description="ساخت اسلایدر جدید. دقت کنید **حتماً باید از FormData استفاده کنید** چون حاوی فایل عکس است.",
        responses={201: SliderDashboardSerializer},
        examples=[
            OpenApiExample(
                name="مثال دیتای خروجی موفق",
                value={
                    "id": 2,
                    "name": "کمپین بهاره",
                    "image_url": "http://api.printoo24.com/media/slider/spring.png",
                    "link": "https://printoo24.com/spring",
                    "created_at": "2023-12-01T12:00:00Z",
                    "updated_at": "2023-12-01T12:00:00Z"
                },
                response_only=True,
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        instance = self.service.create_slider(data=serializer.validated_data)
        
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

    # ==========================================
    # ویرایش اسلایدر (PUT)
    # ==========================================
    @extend_schema(
        summary="ویرایش کامل اسلایدر (PUT)",
        description="ویرایش اطلاعات اسلایدر. اگر عکس جدیدی ارسال شود، جایگزین عکس قبلی می‌گردد. دیتا باید FormData باشد.",
        responses={200: SliderDashboardSerializer}
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        updated_instance = self.service.update_slider(
            instance_or_pk=instance,
            data=serializer.validated_data
        )

        return Response(self.get_serializer(updated_instance).data, status=status.HTTP_200_OK)

    # ==========================================
    # حذف اسلایدر (DELETE)
    # ==========================================
    @extend_schema(
        summary="حذف اسلایدر",
        description="شناسه (ID) اسلایدر را در URL پاس دهید تا اسلایدر و عکس متصل به آن حذف شود.",
        responses={204: None}
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.delete_slider(instance_or_pk=instance)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    

