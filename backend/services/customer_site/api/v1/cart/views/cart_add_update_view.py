from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from ..serializers import (
    AddToCartSerializer,
    CartItemUpdateSerializer,
    CartItemSerializer # خروجی نهایی برای نمایش آیتم ساخته شده
)
from apps.cart.services import AddToCartService, CartItemUpdateService

# ===== Add To Cart View ===== #
@extend_schema(tags=["Cart"])
class AddToCartView(GenericAPIView):
    """
    POST /api/v1/cart/add/
    افزودن محصول به سبد خرید (بدون آپلود فایل).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AddToCartSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        try:
            service = AddToCartService(user=request.user)
            
            # فراخوانی سرویس (فقط اسلاگ و انتخاب‌ها)
            cart_item = service.execute(
                product_slug=validated_data["product_slug"],
                selections=validated_data["selections"]
            )
            
            # بازگشت آیتم ساخته شده
            response_serializer = CartItemSerializer(cart_item, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            # مدیریت خطای تمیز برای فرانت
            error_msg = str(e)
            if hasattr(e, 'detail'): error_msg = e.detail
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

# ===== Cart Item Update View ===== #
@extend_schema(tags=["Cart"])
class CartItemUpdateView(GenericAPIView):
    """
    PATCH /api/v1/cart/items/{item_id}/
    ویرایش تعداد یا ویژگی‌های یک آیتم.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemUpdateSerializer

    def patch(self, request, item_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = CartItemUpdateService(user=request.user)
            
            # ارسال داده‌های جدید به سرویس آپدیت
            updated_item = service.update(
                cart_item_id=item_id,
                raw_data=serializer.validated_data
            )
            
            return Response({
                "message": "سبد خرید با موفقیت بروزرسانی شد.",
                "item_id": updated_item.id,
                "new_price": updated_item.price,
                "quantity": updated_item.quantity
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
