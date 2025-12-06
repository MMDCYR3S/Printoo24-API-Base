from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from core.domain.general import SliderDomainService
from .serializers import SliderSerializer

# ===== Slider ViewSet (Customer Side) ===== #
@extend_schema(tags=['Slider'])
class SliderViewSet(viewsets.ViewSet):
    """
    نمایش اسلایدرهای صفحه اصلی برای مشتریان.
    این ویو فقط قابلیت خواندن (Read-Only) دارد.
    """
    permission_classes = [AllowAny] # همه کاربران (حتی مهمان) باید ببینند

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SliderDomainService()

    @extend_schema(responses=SliderSerializer(many=True), summary="دریافت لیست اسلایدرها")
    def list(self, request):
        queryset = self.service.get_all()
        serializer = SliderSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)