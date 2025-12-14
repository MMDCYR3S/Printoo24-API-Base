from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes, OpenApiParameter

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
    
    @extend_schema(
        summary="افزودن آیتم به سبد خرید",
        description="""
        این متد یک محصول را بر اساس اسلاگ و تنظیمات انتخابی (Selections) به سبد خرید اضافه می‌کند.
        
        **نکات مهم:**
        * `selections`: یک آبجکت است که جزئیات سفارش (تعداد، سایز، آپشن‌ها) در آن قرار می‌گیرد.
        * `option_value_ids`: لیست شناسه (ID) مقادیر ویژگی‌های انتخاب شده (مثلاً ID کاغذ گلاسه).
        * اگر `width` و `height` بفرستید، `size_id` باید `null` باشد (و برعکس).
        """,
        request=AddToCartSerializer,
        responses={201: CartItemSerializer, 400: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Standard Product Example',
                summary='مثال محصول استاندارد (کارت ویزیت)',
                description='افزودن ۱۰۰۰ عدد کارت ویزیت با سایز مشخص و دو آپشن (مثلاً جنس کاغذ و روکش).',
                value={
                    "product_slug": "business-card-laminate",
                    "selections": {
                        "quantity": 1000,
                        "size_id": 5,
                        "has_design": True,
                        "option_value_ids": [101, 205],
                        "width": 0,
                        "height": 0
                    }
                },
                request_only=True
            ),
            OpenApiExample(
                'Custom Size Product',
                summary='مثال محصول متراژی (بنر)',
                description='افزودن بنر با ابعاد دلخواه (۳ در ۱ متر).',
                value={
                    "product_slug": "large-banner",
                    "selections": {
                        "quantity": 1,
                        "size_id": None,
                        "width": 300,
                        "height": 100,
                        "has_design": False,
                        "option_value_ids": [310]
                    }
                },
                request_only=True
            )
        ]
    )
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

    @extend_schema(
        summary="ویرایش تعداد یا ویژگی‌ها",
        description="""
        برای ویرایش هر بخشی از آیتم (مثلاً تغییر تعداد یا تغییر آپشن‌ها)، فیلد مربوطه را ارسال کنید.
        """,
        parameters=[
            OpenApiParameter("item_id", OpenApiTypes.INT, OpenApiParameter.PATH, description="شناسه آیتم سبد خرید")
        ],
        request=CartItemUpdateSerializer,
        responses={
            200: OpenApiTypes.OBJECT, 
            400: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                'Update Quantity Only',
                summary='تغییر تعداد',
                value={"quantity": 2000}
            ),
            OpenApiExample(
                'Update Options',
                summary='تغییر ویژگی‌ها',
                value={
                    "quantity": 1000,
                    "option_value_ids": [102, 205] 
                }
            )
        ]
    )
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
