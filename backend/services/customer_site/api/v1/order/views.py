from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.views import extend_schema

from apps.order.services import CreateOrderFromCartService
from apps.order.exceptions import (
    EmptyCartError,
    InsufficientFundsError,
    OrderCreationError
)
from .serializers import OrderSerializer
from core.models import Address

# ===== Create Order View ===== #
@extend_schema(tags=["Order"])
class CreateOrderView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        """
        ایجاد سفارش پس از اعتبارسنجی
        """
        # ===== اجرای سریالایزر و اعتبارسنجی ====== #
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        address_instance = input_serializer.validated_data.get('address')

        try:
            # ===== ساخت سرویس ثبت سفارش ===== #
            service = CreateOrderFromCartService()
            order = service.execute(
                user=request.user, 
                address=address_instance
            )
            
            # ===== ایجاد شیء خروجی ===== #
            output_serializer = self.get_serializer(order)
            
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        except EmptyCartError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except InsufficientFundsError as e:
            return Response({"error": str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED)
            
        except OrderCreationError as e:
            # ===== اگر خیر خطا رخ داده باشد ===== #
            return Response({"error": "خطایی در ثبت سفارش رخ داد."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
