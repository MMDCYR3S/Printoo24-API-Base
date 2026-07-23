from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample

from apps.home.models import SiteMedia
from ..serializers import SiteMediaSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Dashboard-Media'],
        summary="لیست تمام رسانه‌ها",
        description="دریافت لیست کامل رسانه‌های سایت. فقط برای ادمین.",
        responses={
            200: OpenApiResponse(
                response=SiteMediaSerializer(many=True),
                examples=[
                    OpenApiExample(
                        name="لیست رسانه‌ها",
                        value=[
                            {
                                "id": 1,
                                "file": "https://example.com/media/site_media/banner.jpg",
                                "link": "https://example.com/landing",
                                "is_active": True,
                                "created_at": "2024-01-15T10:30:00Z",
                                "updated_at": "2024-01-15T10:30:00Z"
                            },
                            {
                                "id": 2,
                                "file": "https://example.com/media/site_media/promo.gif",
                                "link": None,
                                "is_active": False,
                                "created_at": "2024-01-10T08:00:00Z",
                                "updated_at": "2024-01-12T14:20:00Z"
                            }
                        ],
                        response_only=True,
                    )
                ]
            ),
            401: OpenApiResponse(description="احراز هویت نشده"),
        },
    ),
    retrieve=extend_schema(
        tags=['Dashboard-Media'],
        summary="دریافت یک رسانه",
        responses={
            200: OpenApiResponse(
                response=SiteMediaSerializer,
                examples=[
                    OpenApiExample(
                        name="جزئیات رسانه",
                        value={
                            "id": 1,
                            "file": "https://example.com/media/site_media/banner.jpg",
                            "link": "https://example.com/landing",
                            "is_active": True,
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-01-15T10:30:00Z"
                        },
                        response_only=True,
                    )
                ]
            ),
            401: OpenApiResponse(description="احراز هویت نشده"),
            404: OpenApiResponse(description="رسانه یافت نشد"),
        },
    ),
    create=extend_schema(
        tags=['Dashboard-Media'],
        summary="آپلود رسانه جدید",
        description="""
        آپلود فایل تصویری یا گیف جدید با `multipart/form-data`.
        - حداکثر حجم فایل: **5MB**
        - فرمت‌های مجاز: `jpg`, `jpeg`, `png`, `gif`, `webp`
        - اگر `is_active=true` باشد، سایر رسانه‌ها غیرفعال می‌شوند.
        """,
        request=SiteMediaSerializer,
        responses={
            201: OpenApiResponse(
                response=SiteMediaSerializer,
                examples=[
                    OpenApiExample(
                        name="رسانه ایجاد شد",
                        value={
                            "id": 3,
                            "file": "https://example.com/media/site_media/new_banner.png",
                            "link": "https://example.com/sale",
                            "is_active": True,
                            "created_at": "2024-02-01T09:00:00Z",
                            "updated_at": "2024-02-01T09:00:00Z"
                        },
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                description="داده‌های نامعتبر",
                examples=[
                    OpenApiExample(
                        name="خطای اعتبارسنجی",
                        value={"file": ["حجم فایل نباید بیشتر از 5MB باشد."]},
                        response_only=True,
                    )
                ]
            ),
            401: OpenApiResponse(description="احراز هویت نشده"),
        },
        examples=[
            OpenApiExample(
                name="آپلود با فعال‌سازی",
                summary="فایل آپلود میشه و is_active=true میشه",
                description="فرانت باید با FormData بفرسته. بقیه رسانه‌ها غیرفعال میشن.",
                value={
                    "file": "<انتخاب فایل از input type=file>",
                    "link": "https://example.com/sale",
                    "is_active": True
                },
                request_only=True,
            ),
            OpenApiExample(
                name="آپلود بدون فعال‌سازی",
                summary="فایل آپلود میشه ولی نمایش داده نمیشه",
                value={
                    "file": "<انتخاب فایل از input type=file>",
                    "link": "",
                    "is_active": False
                },
                request_only=True,
            ),
        ],
    ),
    update=extend_schema(
        tags=['Dashboard-Media'],
        summary="ویرایش کامل رسانه (PUT)",
        description="""
        تمام فیلدها باید ارسال شوند.
        - اگر فایل جدید بفرستی، فایل قبلی از سرور حذف میشه.
        - اگر `is_active=true` بفرستی، بقیه رسانه‌ها غیرفعال میشن.
        """,
        request=SiteMediaSerializer,
        responses={
            200: OpenApiResponse(
                response=SiteMediaSerializer,
                examples=[
                    OpenApiExample(
                        name="رسانه آپدیت شد",
                        value={
                            "id": 1,
                            "file": "https://example.com/media/site_media/updated_banner.jpg",
                            "link": "https://example.com/new-landing",
                            "is_active": True,
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-02-05T11:45:00Z"
                        },
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(description="داده‌های نامعتبر"),
            401: OpenApiResponse(description="احراز هویت نشده"),
            404: OpenApiResponse(description="رسانه یافت نشد"),
        },
        examples=[
            OpenApiExample(
                name="ویرایش کامل با فایل جدید",
                value={
                    "file": "<فایل جدید - فایل قبلی حذف میشه>",
                    "link": "https://example.com/new-landing",
                    "is_active": True
                },
                request_only=True,
            ),
            OpenApiExample(
                name="ویرایش کامل بدون تغییر فایل",
                description="اگر فایل نفرستی، فایل قبلی دست نخورده میمونه.",
                value={
                    "link": "https://example.com/new-landing",
                    "is_active": False
                },
                request_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        tags=['Dashboard-Media'],
        summary="ویرایش جزئی رسانه (PATCH)",
        description="فقط فیلدهایی که میخوای تغییر بده رو بفرست.",
        request=SiteMediaSerializer,
        responses={
            200: OpenApiResponse(
                response=SiteMediaSerializer,
                examples=[
                    OpenApiExample(
                        name="رسانه جزئی آپدیت شد",
                        value={
                            "id": 1,
                            "file": "https://example.com/media/site_media/banner.jpg",
                            "link": "https://example.com/updated-link",
                            "is_active": False,
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-02-05T12:00:00Z"
                        },
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(description="داده‌های نامعتبر"),
            401: OpenApiResponse(description="احراز هویت نشده"),
            404: OpenApiResponse(description="رسانه یافت نشد"),
        },
        examples=[
            OpenApiExample(
                name="فقط لینک عوض میشه",
                value={"link": "https://example.com/updated-link"},
                request_only=True,
            ),
            OpenApiExample(
                name="فقط وضعیت نمایش عوض میشه",
                value={"is_active": True},
                request_only=True,
            ),
            OpenApiExample(
                name="فایل و لینک با هم عوض میشن",
                value={
                    "file": "<فایل جدید>",
                    "link": "https://example.com/new-link"
                },
                request_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        tags=['Dashboard-Media'],
        summary="حذف رسانه",
        description="رسانه و فایل فیزیکی آن از سرور حذف می‌شود. این عملیات برگشت‌پذیر نیست.",
        responses={
            204: OpenApiResponse(description="رسانه با موفقیت حذف شد - بدون بدی در response"),
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
        """
        مدیریت منطق ذخیره‌سازی هنگام ساخت مدیای جدید
        """
        with transaction.atomic():
            if serializer.validated_data.get('is_active') is True:
                SiteMedia.objects.update(is_active=False)
            serializer.save()

    def perform_update(self, serializer):
        """
        مدیریت آپدیت و جایگزینی فایل
        """
        instance = self.get_object()
        with transaction.atomic():
            if serializer.validated_data.get('is_active') is True:
                SiteMedia.objects.exclude(pk=instance.pk).update(is_active=False)
            new_file = serializer.validated_data.get('file')
            if new_file and instance.file and new_file != instance.file:
                instance.file.delete(save=False)
            serializer.save()

    def perform_destroy(self, instance):
        """
        حذف فایل فیزیکی قبل از حذف رکورد از دیتابیس
        """
        if instance.file:
            instance.file.delete(save=False)
        instance.delete()


# ==========================================
# 2. View پابلیک
# ==========================================
@extend_schema_view(
    list=extend_schema(
        tags=['Public-Media'],
        summary="لیست رسانه‌های عمومی",
        responses={
            200: OpenApiResponse(
                response=SiteMediaSerializer(many=True),
                examples=[
                    OpenApiExample(
                        name="لیست رسانه‌های عمومی",
                        value=[
                            {
                                "id": 1,
                                "file": "https://example.com/media/site_media/banner.jpg",
                                "link": "https://example.com/landing",
                                "is_active": True,
                                "created_at": "2024-01-15T10:30:00Z",
                                "updated_at": "2024-01-15T10:30:00Z"
                            }
                        ],
                        response_only=True,
                    )
                ]
            ),
        },
    ),
    retrieve=extend_schema(
        tags=['Public-Media'],
        summary="دریافت یک رسانه عمومی",
        responses={
            200: OpenApiResponse(
                response=SiteMediaSerializer,
                examples=[
                    OpenApiExample(
                        name="جزئیات رسانه عمومی",
                        value={
                            "id": 1,
                            "file": "https://example.com/media/site_media/banner.jpg",
                            "link": "https://example.com/landing",
                            "is_active": True,
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-01-15T10:30:00Z"
                        },
                        response_only=True,
                    )
                ]
            ),
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