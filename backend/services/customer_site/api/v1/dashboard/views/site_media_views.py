from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from apps.home.services import SiteMediaService
from ..serializers import SiteMediaSerializer

# ==========================================
# 1. View داشبورد (مخصوص مدیریت - CRUD کامل)
# ==========================================
@extend_schema(tags=['Dashboard-Media'])
class SiteMediaDashboardViewSet(viewsets.ModelViewSet):
    """
    مدیریت رسانه‌های سایت برای داشبورد ادمین.
    """
    serializer_class = SiteMediaSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated] # فقط ادمین یا کاربران لاگین شده بر اساس پرمیشن شما

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SiteMediaService()

    def get_queryset(self):
        return self.service.get_all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create_media(data=serializer.validated_data)
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_instance = self.service.update_media(instance_or_pk=instance, data=serializer.validated_data)
        return Response(self.get_serializer(updated_instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.delete_media(instance_or_pk=instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==========================================
# 2. View پابلیک (مخصوص کاربران ثبت‌نام نکرده)
# ==========================================
@extend_schema(tags=['Public-Media'])
class SiteMediaPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    دریافت رسانه‌ها برای کاربران عمومی (فقط خواندنی).
    حتی نیازی به توکن ندارد.
    """
    serializer_class = SiteMediaSerializer
    permission_classes = [AllowAny] # اجازه دسترسی به همه حتی کاربران میهمان

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SiteMediaService()

    def get_queryset(self):
        return self.service.get_all()
