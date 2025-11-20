from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from ..serializers import CartItemUpdateSerializer
from apps.cart.services import CartItemUpdateService

# ======= Cart Item Update View ======= #
@extend_schema(tags=["Cart"])
class CartItemUpdateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemUpdateSerializer

    def patch(self, request, item_id):
        """
        ویرایش سبد خرید با استفاده از سرویس و فیلدهای مورد نیاز
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # ===== ایجاد سرویس بروزرسانی ===== #
        service = CartItemUpdateService(user=request.user)
        
        try:
            updated_item = service.update(
                cart_item_id=item_id,
                data=serializer.validated_data
            )
            
            return Response({
                "message": "مشخصات محصول در سبد خرید با موفقیت ویرایش شد.",
                "price": updated_item.price
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
