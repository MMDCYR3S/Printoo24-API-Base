from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.views import extend_schema

from apps.cart.services import CartListService, CartItemDetailService
from ..serializers import CartListSerializer, CartItemSerializer
from core.common.cart import (
    CartItemRepository,
    CartItemService
)

# ======== Cart List View ======== #
@extend_schema(tags=['Cart'])
class CartListView(GenericAPIView):
    """
    نمایش لیست سبد خرید هر کاربر
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartListSerializer

    def get(self, request):
        # ===== ایجاد سرویس نمایش لیست سبد خرید ===== #
        service = CartListService()
        result = service.get_user_cart_items(request.user)
        # ===== نمایش لیست سبد خرید ===== # 
        cart = result['cart']
        items = result['items']
        
        cart.prefetched_items = items 
        
        serializer = self.get_serializer(cart)
        # ===== واکشی اطلاعات از سریالایزر بعد از تبدیل داده به JSON ===== #
        response_data = serializer.data
        response_data['items'] = CartItemSerializer(items, many=True).data
        
        return Response(response_data, status=status.HTTP_200_OK)

# ======== Cart Item Detail View ======== #
@extend_schema(tags=['Cart'])
class CartItemDetailView(GenericAPIView):
    """
    نمایش جزئیات هر آیتم سبد خرید
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer
    
    def get(self, request, item_id):
        # ===== ایجاد سرویس مربوط به نمایش جزئیات آیتم سبد خرید ===== #
        service = CartItemDetailService()
        
        try:
            item = service.get_item_detail(item_id=item_id, user=request.user)
            serializer = self.get_serializer(item)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response(
                {"detail": "آیتم یافت نشد."}, 
                status=status.HTTP_404_NOT_FOUND
            )
    