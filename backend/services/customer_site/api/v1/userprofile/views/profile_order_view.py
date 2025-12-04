from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from drf_spectacular.utils import extend_schema

from apps.userprofile.services import UserOrderListService
from ..serializers import OrderWithDetailsSerializer, OrderSerializer

# ===== User Order List APIView ===== #
@extend_schema(tags=["Profile"])
class UserOrderListAPIView(APIView):
    """
    لیست سابقه سفارشات مشتری (خلاصه).
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service = UserOrderListService()

    def get(self, request):
        orders = self._service.get_user_orders(request.user.id)
        
        serializer = OrderSerializer(
            orders, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

# ===== User Order Detail APIView ===== #
@extend_schema(tags=["Profile"])
class UserOrderDetailAPIView(APIView):
    """
    جزئیات کامل سفارش مشتری (شامل فایل‌ها و آیتم‌ها).
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service = UserOrderListService()

    def get(self, request, order_id):
        try:
            order = self._service.get_order_detail(request.user.id, order_id)
            
            # ===== اصلاح حیاتی: ارسال context ===== #
            # این کار باعث می‌شود متد get_file_url در سریالایزر بتواند لینک کامل بسازد
            serializer = OrderWithDetailsSerializer(
                order, 
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        except (ValidationError, NotFound) as e:
            # مدیریت خطای تمیز
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': 'خطایی رخ داد.', 'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
