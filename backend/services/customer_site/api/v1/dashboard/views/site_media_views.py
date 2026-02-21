from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from apps.home.models import SiteMedia
from ..serializers import SiteMediaSerializer

# ==========================================
# 1. View داشبورد (مخصوص مدیریت - CRUD کامل)
# ==========================================
@extend_schema(tags=['Dashboard-Media'])
class SiteMediaDashboardViewSet(viewsets.ModelViewSet):
    """
    مدیریت رسانه‌های سایت برای داشبورد ادمین.
    بدون لایه سرویس - مدیریت مستقیم مدل.
    """
    serializer_class = SiteMediaSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    
    # جایگزین get_queryset
    queryset = SiteMedia.objects.all()

    def perform_create(self, serializer):
        """
        مدیریت منطق ذخیره‌سازی هنگام ساخت مدیای جدید
        """
        with transaction.atomic():
            # اگر قرار است فعال باشد، بقیه رکوردها را غیرفعال می‌کنیم
            if serializer.validated_data.get('is_active') is True:
                # استفاده از ORM جنگو به جای متد کاستوم منیجر برای اطمینان
                SiteMedia.objects.update(is_active=False)
            
            # ذخیره رکورد جدید
            serializer.save()

    def perform_update(self, serializer):
        """
        مدیریت آپدیت و جایگزینی فایل
        """
        instance = self.get_object()
        
        with transaction.atomic():
            # اگر این مدیا دارد فعال می‌شود، بقیه (به جز خودش) را غیرفعال کن
            if serializer.validated_data.get('is_active') is True:
                SiteMedia.objects.exclude(pk=instance.pk).update(is_active=False)

            # بررسی اینکه آیا فایل جدیدی ارسال شده است یا خیر
            new_file = serializer.validated_data.get('file')
            # در صورتی که فایل جدیدی آمده باشد، فایل قبلی را از هارد پاک کن
            if new_file and instance.file and new_file != instance.file:
                instance.file.delete(save=False)

            # اعمال تغییرات روی دیتابیس
            serializer.save()

    def perform_destroy(self, instance):
        """
        حذف فایل فیزیکی قبل از حذف رکورد از دیتابیس
        """
        if instance.file:
            instance.file.delete(save=False)
        instance.delete()


# ==========================================
# 2. View پابلیک (مخصوص کاربران ثبت‌نام نکرده)
# ==========================================
@extend_schema(tags=['Public-Media'])
class SiteMediaPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    دریافت رسانه‌ها برای کاربران عمومی (فقط خواندنی).
    """
    serializer_class = SiteMediaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        در سرویس شما برای متد get_all همان لیست کل داده‌ها برگردانده می‌شد.
        اگر می‌خواهید برای پابلیک 'فقط عکس‌های فعال' نمایش داده شوند (مانند get_active_for_display):
        return SiteMedia.objects.filter(is_active=True)
        """
        return SiteMedia.objects.all() # در صورت داشتن متد اختصاصی در منیجر: SiteMedia.objects.get_all_media()