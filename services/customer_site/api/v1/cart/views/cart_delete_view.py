from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.views import extend_schema


from apps.cart.services import CartItemDeleteService, CartClearService

# ===== Cart Item Delete View ===== #
@extend_schema(
    tags=["Cart"],
    operation_id="Delete Cart Item",
    description="حذف یک آیتم مشخص از سبد خرید کاربر."
)
class CartItemDeleteView(GenericAPIView):
    """ 
    ارسال درخواست حذف یک آیتم در سبد خرید از طرف کاربر به سیستم
    """
    
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, item_id: int, *args, **kwargs):
        """
        حذف یک آیتم از سبد خرید کاربر.
        """
        user = request.user
        
        try:
            # ===== سرویس حذف آیتم سبد خرید ===== #
            service = CartItemDeleteService(user=user)
            service.delete(item_id=item_id)
            return Response({"detail": "آیتم با موفقیت حذف شد."}, status=status.HTTP_204_NO_CONTENT)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        
# ===== Cart Clear View ===== #
@extend_schema(
    tags=["Cart"],
    operation_id="Clear Cart",
    description="پاکسازی کلی سبد خرید کاربر و حذف تمام آیتم‌ها."
)
class CartClearView(GenericAPIView):
    """
    پاکسازی کلی سبد خرید کاربر و حذف تمام آیتم‌ها
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        """
        حذف تمام آیتم‌های سبد خرید کاربر.
        """
        user = request.user
        
        try:
            # ===== سرویس پاکسازی سبد خرید ===== #
            service = CartClearService(user=user)
            service.clear()
            return Response({"detail": "تمام آیتم‌های سبد خرید با موفقیت حذف شدند."}, status=status.HTTP_204_NO_CONTENT)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
