from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.views import extend_schema

from apps.operations.services import OrderDetailAppService
from ..serializers import (
    AdminOrderDetailSerializer,
    DesignerOrderDetailSerializer,
    FinanceOrderDetailSerializer,
    LogisticsOrderDetailSerializer,
    BaseOrderDetailSerializer,
)
# ========== Order Detail View ========== #
@extend_schema(tags=['Order'])
class OrderDetailView(GenericAPIView):
    """
    دریافت جزئیات کامل سفارش براساس نوع نقش کاربر
    """
    permission_classes = [IsAuthenticated]

    # ===== کانفیگ داینامیک سریالایزرها ===== #
    SERIALIZER_MAP = {
        'admin_internal': AdminOrderDetailSerializer,
        'designer': DesignerOrderDetailSerializer,
        'finance': FinanceOrderDetailSerializer,
        'warehouse': LogisticsOrderDetailSerializer,
        'print': DesignerOrderDetailSerializer,
        'qc': DesignerOrderDetailSerializer,
    }

    def get_serializer_class(self, user, role_code):
        """
        انتخاب هوشمند سریالایزر بر اساس نقش کاربر
        """
        # ===== اولویت اول: کاربر ادمین ===== #
        if user.is_superuser:
            return AdminOrderDetailSerializer
        # ===== اولویت دوم: کاربر با نقش محدود ===== #
        return self.SERIALIZER_MAP.get(role_code, BaseOrderDetailSerializer)

    def get(self, request, pk):
        """
        دریافت اطلاعات سفارش
        """
        service = OrderDetailAppService()
        # ===== دریافت اطلاعات ===== #
        order, role_code = service.get_order_detail(request.user, pk)
        # ===== انتخاب سریالایزر ===== #
        SerializerClass = self.get_serializer_class(request.user, role_code)
        # ===== ساخت سریالایزر =====
        serializer = SerializerClass(order, context={'request': request})
        return Response(serializer.data)