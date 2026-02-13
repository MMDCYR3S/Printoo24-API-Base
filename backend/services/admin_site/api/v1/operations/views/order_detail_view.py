from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.views import extend_schema

from apps.operations.services import OrderDetailAppService
from ..serializers import (
    UniversalOrderDetailSerializer
)
# ========== Order Detail View ========== #
@extend_schema(tags=['Order - List For Staffs'])
class OrderDetailView(GenericAPIView):
    """
    دریافت جزئیات سفارش با یک سریالایزر واحد برای همه نقش‌ها.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UniversalOrderDetailSerializer 

    def get(self, request, pk):
        service = OrderDetailAppService()
        
        try:
            order = service.get_order_detail(request.user, pk)

            serializer = self.get_serializer(order)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)
        except Exception as e:
            from rest_framework.exceptions import PermissionDenied
            if isinstance(e, PermissionDenied):
                return Response({"detail": str(e)}, status=403)
            print(f"Server Error: {e}") 
            raise e
