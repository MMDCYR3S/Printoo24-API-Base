from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.views import extend_schema

from apps.cart.services import CartListService, CartItemDetailService
from ..serializers import CartListSerializer, CartItemSerializer, CartItemDetailSerializer

# ======== Cart List View ======== #
@extend_schema(tags=['Cart'])
class CartListView(GenericAPIView):
    """
    نمایش لیست سبد خرید (پشتیبانی از کاربر مهمان و عضو).
    """
    permission_classes = [AllowAny]
    serializer_class = CartListSerializer

    @extend_schema(
        summary="مشاهده سبد خرید",
        responses={200: CartListSerializer}
    )
    def get(self, request):
        
        # ===== تشخیص کاربر ===== #
        user = request.user if request.user.is_authenticated else None
        
        # ===== تشخیص شناسه نشست ===== #
        session_key = request.session.session_key
        
        # ===== ایجاد سرویس ===== #
        service = CartListService()
        result = service.get_cart_details(user=user, session_key=session_key)
        
        # ===== نمایش نتیجه ===== #
        cart = result['cart']
        items = result['items']
        
        # ===== اگر سبد خرید وجود نداشت ===== #
        if not cart:
            return Response({
                "id": None,
                "items": [],
                "total_price": 0,
                "updated_at": None
            }, status=status.HTTP_200_OK)
            
        # ===== دریافت سبد خرید و نمایش نتیجه ===== #
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ======== Cart Item Detail View ======== #
@extend_schema(tags=['Cart'])
class CartItemDetailView(GenericAPIView):
    """
    نمایش جزئیات یک آیتم خاص.
    """
    permission_classes = [AllowAny]
    serializer_class = CartItemDetailSerializer
    
    @extend_schema(summary="دریافت جزئیات آیتم")
    def get(self, request, item_id):
        # ===== تشخیص کاربر ===== #
        user = request.user if request.user.is_authenticated else None
        
        # ===== تشخیص شناسه نشست ===== #
        session_key = request.session.session_key
        
        # ===== ایجاد سرویس ===== #
        service = CartItemDetailService()
        
        # ===== دریافت جزئیات ===== #
        try:
            item = service.get_item_detail(
                item_id=item_id, 
                user=user, 
                session_key=session_key
            )
            
            serializer = self.get_serializer(item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # ===== در صورتی که آیتم وجود نداشت ===== #
        except ObjectDoesNotExist:
            return Response(
                {"detail": "آیتم یافت نشد یا دسترسی ندارید."}, 
                status=status.HTTP_404_NOT_FOUND
            )
