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
    دریافت جزئیات کامل سفارش براساس نوع نقش کاربر.
    سیستم به صورت هوشمند و بر اساس تنظیمات نقش (View Mode) سریالایزر مناسب را انتخاب می‌کند.
    """
    permission_classes = [IsAuthenticated]

    VIEW_MODE_SERIALIZERS = {
        'full': AdminOrderDetailSerializer,
        'design': DesignerOrderDetailSerializer,
        'finance': FinanceOrderDetailSerializer,
        'logistics': LogisticsOrderDetailSerializer,
        'simple': BaseOrderDetailSerializer
    }

    def get_serializer_class(self, view_mode):
        """ انتخاب سریالایزر بر اساس مد نمایش نقش """
        return self.VIEW_MODE_SERIALIZERS.get(view_mode, BaseOrderDetailSerializer)

    def get(self, request, pk):
        """
        دریافت اطلاعات سفارش.
        سرویس علاوه بر دیتا، view_mode نقش کاربر را هم برمی‌گرداند.
        """
        service = OrderDetailAppService()
        
        try:
            order, view_mode_code = service.get_order_detail(request.user, pk)

            if view_mode_code == 'superuser':
                SerializerClass = AdminOrderDetailSerializer
            else:
                SerializerClass = self.get_serializer_class(view_mode_code)
            
            serializer = SerializerClass(order, context={'request': request})
            return Response(serializer.data)
            
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)
        except Exception as e:
            from rest_framework.exceptions import PermissionDenied
            if isinstance(e, PermissionDenied):
                return Response({"detail": str(e)}, status=403)
            raise e
