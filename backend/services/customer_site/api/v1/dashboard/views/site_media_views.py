from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample

from apps.home.models import SiteMedia
from ..serializers import SiteMediaSerializer


# ==========================================
# 1. View داشبورد (مخصوص مدیریت - CRUD کامل)
# ==========================================
@extend_schema_view(
    list=extend_schema(
        tags=['Dashboard-Media'],
        summary="لیست تمام رسانه‌ها",
        description="دریافت لیست کامل رسانه‌های سایت. فقط برای ادمین.",
        responses={
            200: SiteMediaSerializer(many=True),
            401: OpenApiResponse(description="احراز هویت نشده"),
        },
    ),
    retrieve=extend_schema(
        tags=['Dashboard-Media'],
        summary="دریافت یک رسانه",
        description="دریافت جزئیات یک رسانه خاص بر اساس ID.",
        responses={
            200: SiteMediaSerializer,
            401: OpenApiResponse(description="احراز هویت نشده"),
            404: OpenApiResponse(description="رسانه یافت نشد"),
        },
    ),
    create=extend_schema(
        tags=['Dashboard-Media'],
        summary="آپلود رسانه جدید",
        description="""
        آپلود فایل تصویری یا گیف جدید.
        - حداکثر حجم فایل: 5MB
        - فرمت‌های مجاز: jpg, jpeg, png, gif, webp
        - در صورت فعال بودن `is_active`، سایر رسانه‌ها غیرفعال می‌شوند.
        """,
        request=SiteMediaSerializer,
        responses={
            201: SiteMediaSerializer,
            400: OpenApiResponse(description="داده‌های نامعتبر"),
            401: OpenApiResponse(description="احراز هویت نشده"),
        },
        examples=[
            OpenApiExample(
                name="آپلود رسانه فعال",
                summary="آپلود یک رسانه و فعال کردن آن",
                description="با ارسال is_active=true رسانه‌های قبلی غیرفعال می‌شوند.",
                value={"file": "<binary>", "link": "https://example.com", "is_active": True},
                request_only=True,
            ),
            OpenApiExample(
                name="آپلود رسانه غیرفعال",
                summary="آپلود رسانه بدون فعال‌سازی",
                value={"file": "<binary>", "link": "", "is_active": False},
                request_only=True,
            ),
        ],
    ),
    update=extend_schema(
        tags=['Dashboard-Media'],
        summary="ویرایش کامل رسانه",
        description="""
        به‌روزرسانی کامل اطلاعات رسانه (PUT).
        - در صورت ارسال فایل جدید، فایل قبلی از هارد حذف می‌شود.
        - در صورت فعال‌سازی، سایر رسانه‌ها غیرفعال می‌شوند.
        """,
        request=SiteMediaSerializer,
        responses={
            200: SiteMediaSerializer,
            400: OpenApiResponse(description="داده‌های نامعتبر"),
            401: OpenApiResponse(description="احراز هویت نشده"),
            404: OpenApiResponse(description="رسانه یافت نشد"),
        },
    ),
    partial_update=extend_schema(
        tags=['Dashboard-Media'],
        summary="ویرایش جزئی رسانه",
        description="""
        به‌روزرسانی بخشی از اطلاعات رسانه (PATCH).
        - فقط فیلدهای ارسال‌شده به‌روز می‌شوند.
        - در صورت ارسال فایل جدید، فایل قبلی از هارد حذف می‌شود.
        """,
        request=SiteMediaSerializer,
        responses={
            200: SiteMediaSerializer,
            400: OpenApiResponse(description="داده‌های نامعتبر"),
            401: OpenApiResponse(description="احراز هویت نشده"),
            404: OpenApiResponse(description="رسانه یافت نشد"),
        },
    ),
    destroy=extend_schema(
        tags=['Dashboard-Media'],
        summary="حذف رسانه",
        description="حذف رسانه و فایل فیزیکی مربوطه از سرور.",
        responses={
            204: OpenApiResponse(description="رسانه با موفقیت حذف شد"),
            401: OpenApiResponse(description="احراز هویت نشده"),
            404: OpenApiResponse(description="رسانه یافت نشد"),
        },
    ),
)
@extend_schema(tags=['Dashboard-Media'])
class SiteMediaDashboardViewSet(viewsets.ModelViewSet):
    """
    مدیریت رسانه‌های سایت برای داشبورد ادمین.
    بدون لایه سرویس - مدیریت مستقیم مدل.
    """
    serializer_class = SiteMediaSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    queryset = SiteMedia.objects.all()

    def perform_create(self, serializer):
        with transaction.atomic():
            if serializer.validated_data.get('is_active') is True:
                SiteMedia.objects.update(is_active=False)
            serializer.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        with transaction.atomic():
            if serializer.validated_data.get('is_active') is True:
                SiteMedia.objects.exclude(pk=instance.pk).update(is_active=False)
            new_file = serializer.validated_data.get('file')
            if new_file and instance.file and new_file != instance.file:
                instance.file.delete(save=False)
            serializer.save()

    def perform_destroy(self, instance):
        if instance.file:
            instance.file.delete(save=False)
        instance.delete()


# ==========================================
# 2. View پابلیک (مخصوص کاربران ثبت‌نام نکرده)
# ==========================================
@extend_schema_view(
    list=extend_schema(
        tags=['Public-Media'],
        summary="لیست رسانه‌های عمومی",
        description="دریافت لیست تمام رسانه‌های سایت برای کاربران عمومی.",
        responses={
            200: SiteMediaSerializer(many=True),
        },
    ),
    retrieve=extend_schema(
        tags=['Public-Media'],
        summary="دریافت یک رسانه عمومی",
        description="دریافت جزئیات یک رسانه خاص برای کاربران عمومی.",
        responses={
            200: SiteMediaSerializer,
            404: OpenApiResponse(description="رسانه یافت نشد"),
        },
    ),
)
@extend_schema(tags=['Public-Media'])
class SiteMediaPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    دریافت رسانه‌ها برای کاربران عمومی (فقط خواندنی).
    """
    serializer_class = SiteMediaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return SiteMedia.objects.all()