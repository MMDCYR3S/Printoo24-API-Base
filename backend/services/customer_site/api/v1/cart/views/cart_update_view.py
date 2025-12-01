from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from ..serializers import CartItemUpdateSerializer
from apps.cart.services import CartItemUpdateService

@extend_schema(tags=["Cart"])
class CartItemUpdateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemUpdateSerializer

    def patch(self, request, item_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = CartItemUpdateService(user=request.user)
        
        try:
            # ارسال داده‌های تمیز شده به سرویس
            updated_item = service.update(
                cart_item_id=item_id,
                raw_data=serializer.validated_data # دیکشنری شامل quantity, width, ...
            )
            
            # پاسخ موفقیت آمیز
            # می‌توانیم کل آیتم را برگردانیم یا فقط قیمت جدید را
            return Response({
                "message": "سبد خرید بروزرسانی شد.",
                "item_id": updated_item.id,
                "new_price": updated_item.price, # قیمت نهایی آپدیت شده
                "quantity": updated_item.quantity
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
