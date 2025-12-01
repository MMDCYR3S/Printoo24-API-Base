from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from ..serializers import (
    AddToCartSerializer,
    CartItemSerializer, # فرض بر این است که این برای خروجی استفاده می‌شود
)
from apps.cart.services import AddToCartService

@extend_schema(tags=["Cart"])
class AddToCartView(GenericAPIView):
    """
    POST /api/v1/cart/add/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AddToCartSerializer
    
    def post(self, request, *args, **kwargs):
        # 1. اعتبارسنجی فرمت داده‌ها با سریالایزر
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        try:
            service = AddToCartService(user=request.user)
            
            # 2. فراخوانی سرویس
            # نکته: validated_data['selections'] اکنون یک دیکشنری تمیز حاوی quantity, width, ... است
            cart_item = service.execute(
                product_slug=validated_data["product_slug"],
                selections=validated_data["selections"], 
                temp_file_names=validated_data.get("temp_file_names", {})
            )
            
            # 3. بازگشت نتیجه
            # برای ریسپانس از سریالایزر مدل CartItem استفاده می‌کنیم
            # (باید مطمئن شوید که CartItemSerializer را جداگانه دارید)
            response_serializer = CartItemSerializer(cart_item, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        except (ValidationError, ValueError) as e:
            # خطاهای بیزنس لاجیک (مثل حداقل تیراژ یا ابعاد غلط)
            return Response({'error': str(e.detail) if hasattr(e, 'detail') else str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
        except Exception as e:
            # خطاهای پیش‌بینی نشده
            return Response({'error': 'خطای سیستمی رخ داده است.', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
