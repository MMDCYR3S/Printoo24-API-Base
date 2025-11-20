import uuid
import os

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.conf import settings
from drf_spectacular.views import extend_schema

from ..serializers import (
    TemporaryFileUploadSerializer,
    AddToCartSerializer,
    CartItemSerializer,
)
from apps.cart.services import AddToCartService

@extend_schema(tags=["Cart"])
class AddToCartView(GenericAPIView):
    """
    ویو برای افزودن یک محصول به سبد خرید کاربر.
    این ویو داده‌ها را اعتبارسنجی کرده و ارکستراتور اصلی (AddToCartService) را فراخوانی می‌کند.
    POST /api/cart/add-item/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AddToCartSerializer
    
    def post(self, request, *args, **kwargs):
        """
        اعتبارسنجی سبد خرید و افزودن محصول مرتبط با ویژگی های انتخاب شده
        توسط کاربر - همچنین انتقال عکس های آپلود شده توسط کاربر از مسیر
        موقت به مدلاسیون مربوط به عکس های آیتم سبد خرید مربوطه
        """
        # ===== اعتبارسنجی ===== #
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        try:
            # ===== ایجاد سرویس اضافه کردن محصول به سبد خرید کاربر ===== #
            service = AddToCartService(user=request.user)
            cart_item = service.execute(
                validated_data["product_slug"],
                validated_data["quantity"],
                validated_data["selections"],
                validated_data["temp_file_names"]
            )
            # ===== ذخیره سازی در سبد خرید و نمایش اطلاعات به کاربر ===== #
            response_serializer = CartItemSerializer(cart_item, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        except (ValidationError, ValueError) as e:
            # ===== بازگشت خطا ===== #
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
    
        except Exception as e:
            # ===== بازگشت خطاهای غیر منتظره ===== #
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
