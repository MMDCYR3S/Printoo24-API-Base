from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.views import extend_schema

from apps.operations.services import OrderListAppService
from apps.operations.filters import OrderFilter
from ..serializers import OrderListSerializer

# ========== Order List View ========== #
@extend_schema(tags=['Order'])
class OrderListView(GenericAPIView):
    """
    API لیست هوشمند سفارشات.
    - فقط سفارشات مجاز (Scope) را نشان می‌دهد.
    - قابلیت جستجو و فیلتر دارد.
    - صفحه‌بندی دارد.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderListSerializer
    # ===== تنظیمات فیلترینگ ===== #
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = OrderFilter
    # ===== تنظیمات جستجو ===== #
    search_fields = ['order_code', 'user__username', 'user__email', 'invoice_order__invoice_number']
    ordering_fields = ['created_at', 'total_price', 'current_status__name']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        این متد توسط GenericAPIView برای Swagger و کارهای داخلی صدا زده می‌شود.
        ما اینجا از سرویس استفاده می‌کنیم.
        """
        service = OrderListAppService()
        return service.get_order_list_for_staff(self.request.user)

    def get(self, request, *args, **kwargs):
        """
        مشاهده لیست سفارشات
        """
        # ===== فیلترینگ ===== #
        queryset = self.get_queryset()
        filtered_queryset = self.filter_queryset(queryset)
        # ===== نمایش ===== #
        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)
