from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.views import extend_schema

from apps.cart.services import CartItemDeleteService, CartClearService
from core.infrastructure.messages import msg_provider

# ===== Cart Item Delete View ===== #
@extend_schema(
    tags=["Cart"],
    summary="حذف آیتم سبد خرید",
    description="حذف یک آیتم خاص. برای کاربر مهمان به طور خودکار از کوکی Session استفاده می‌شود.",
    responses={204: None, 404: None}
)
class CartItemDeleteView(GenericAPIView):
    """ 
    حذف تکی آیتم (Guest + User)
    """
    permission_classes = [AllowAny]
    
    def delete(self, request, item_id: int, *args, **kwargs):
        # ===== یافتن کاربر براساس سشن و اینکه ورود کرده است یا خیر ===== #
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key
        
        try:
            # ===== سرویس حذف آیتم ===== #
            service = CartItemDeleteService(user=user, session_key=session_key)
            service.delete(item_id=item_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        # ===== اگر آیتم وجود نداشت ===== #
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
             return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# ===== Cart Clear View ===== #
@extend_schema(
    tags=["Cart"],
    summary="خالی کردن سبد خرید",
    description="حذف تمام آیتم‌های سبد خرید کاربر جاری (مهمان یا عضو).",
    responses={204: None}
)
class CartClearView(GenericAPIView):
    """
    پاکسازی کامل سبد خرید (Guest + User)
    """
    permission_classes = [AllowAny]
    
    def delete(self, request, *args, **kwargs):
        # ===== یافتن کاربر براساس سشن و اینکه ورود کرده است یا خیر ===== #
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key
        
        try:
            # ===== سرویس پاکسازی ===== #
            service = CartClearService(user=user, session_key=session_key)
            service.clear()
            return Response({"detail": msg_provider.get("cart.S4002")}, status=status.HTTP_204_NO_CONTENT)
            
        # ===== اگر کاربر وجود نداشت ===== #
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
