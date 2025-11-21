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

# ===== Create Order View ===== #
@extend_schema(tags=["Order"])
class CreateOrderView(GenericAPIView):
    """
    ویوی ایجاد سفارش با توجه به سرویس ایجاد سفارش
    منطق این قسمت به این صورت هست که ابتدا سفارش از سمت سبد خرید دریافت شده
    و پردازش می شود. سپس بررسی می شود که آیا موجودی کیف پول کاربر کافی هست یا
    نه. بعد از این موضوع، سفارش ثبت شده، قیمت از موجودی کیف پول مشتری کسر
    می شود و یک تراکنش از نوع کسر وجه و پرداخت برای مشتری در نظر گرفته میشه
    برای اطلاعات بیشتر، به بخش سرویس مراجعه کنید.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        """
        ایجاد سفارش پس از اعتبارسنجی
        """
        try:
            # ===== ایجاد سرویس ثبت سفارش ===== #
            service = CreateOrderFromCartService()
            # ===== اجرای سرویس ===== #
            order = service.execute(user=request.user)
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except EmptyCartError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except InsufficientFundsError as e:
            return Response({"error": str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED)
            
        except OrderCreationError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
