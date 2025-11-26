from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError
from drf_spectacular.views import extend_schema

from apps.userprofile.services import UserOrderListService, UserOrderDetailService
from ..serializers import OrderSummarySerializer, OrderDetailSerializer

# ===== User Order List APIView ===== #
@extend_schema(tags=["Profile"])
class UserOrderListAPIView(APIView):
    """
    لیست سابقه سفارشات مشتری
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service = UserOrderListService()

    def get(self, request):
        orders = self._service.get_user_orders(request.user.id)
        serializer = OrderSummarySerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ===== User Order Detail APIView ===== #
@extend_schema(tags=["Profile"])
class UserOrderDetailAPIView(APIView):
    """
    جزئیات سفارش مشتری
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service = UserOrderDetailService()

    def get(self, request, order_id):
        try:
            order = self._service.get_order_detail(request.user.id, order_id)
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
