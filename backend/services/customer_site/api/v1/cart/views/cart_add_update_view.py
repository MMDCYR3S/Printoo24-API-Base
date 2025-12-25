from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes, OpenApiParameter

from ..serializers import (
    AddToCartSerializer,
    CartItemUpdateSerializer,
    CartItemSerializer
)
from apps.cart.services import AddToCartService, CartItemUpdateService

# ===== Add To Cart View ===== #
@extend_schema(tags=["Cart"])
class AddToCartView(GenericAPIView):
    """
    POST /api/v1/cart/add/
    افزودن محصول به سبد خرید.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AddToCartSerializer
    
    @extend_schema(
        summary="افزودن آیتم به سبد خرید",
        description="""
        این متد محصول را با تمام تنظیمات (تعداد، سایز، آپشن‌ها) به سبد اضافه می‌کند.
        
        **نکات کلیدی:**
        1. **تیراژ:** اگر محصول تیراژ ثابت دارد، `quantity_id` بفرستید. اگر متری/تعدادی است، `quantity` بفرستید.
        2. **آپشن‌ها:** فیلد `options` یک دیکشنری است که کلید آن ID ویژگی است و مقدار آن می‌تواند ID گزینه یا متن باشد.
        """,
        request=AddToCartSerializer,
        responses={201: CartItemSerializer, 400: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Scenario 1: Fixed Quantity (Business Card)',
                summary='سناریو ۱: محصول با تیراژ ثابت (کارت ویزیت)',
                description='انتخاب تیراژ ۱۰۰۰ تایی (ID: 50) + سایز استاندارد + دو آپشن انتخابی.',
                value={
                    "product_id": 105,
                    "selections": {
                        "name": "کارت ویزیت علی بابا",
                        "quantity_id": 50,
                        "size_id": 5,
                        "has_design": True,
                        "options": {
                            "10": 101,
                            "12": 205
                        },
                        "description": "توضیحات تکمیلی"
                    }
                },
                request_only=True
            ),
            OpenApiExample(
                'Scenario 2: Custom Quantity & Text Option',
                summary='سناریو ۲: محصول تعدادی با ورودی متن (لیوان سرامیکی)',
                description='انتخاب ۵ عدد لیوان + نوشتن متن دلخواه روی لیوان.',
                value={
                    "product_id": 200,
                    "selections": {
                        "name": "لیوان سرامیکی",
                        "quantity": 5,
                        "size_id": None,
                        "has_design": False,
                        "options": {
                            "15": "Happy Birthday Sarah",
                            "18": 302
                        },
                        "description": "توضیحات تکمیلی"
                    }
                },
                request_only=True
            ),
            OpenApiExample(
                'Scenario 3: Custom Dimensions (Banner)',
                summary='سناریو ۳: محصول متراژی (بنر)',
                description='سفارش بنر ۳ در ۱ متر (بدون سایز استاندارد).',
                value={
                    "product_id": 300,
                    "selections": {
                        "name": "بنر تبلیغاتی شرکت موز پروران",
                        "quantity": 1, 
                        "width": 300,
                        "height": 100,
                        "has_design": True,
                        "options": {
                            "20": 401
                        },
                        "description": "توضیحات تکمیلی"
                    }
                },
                request_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        """ ایجاد آیتم سبد خرید براساس اطلاعات ارسالی. """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            # ===== فراخوانی سرویس ===== #
            service = AddToCartService(user=request.user)
            
            # ===== اجرای سرویس ===== #
            cart_item = service.execute(
                product_id=data["product_id"],
                selections=data["selections"]
            )
            # ===== بازگشت ===== #
            response_serializer = CartItemSerializer(cart_item, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # مدیریت خطای تمیز برای فرانت
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

# ===== Cart Item Update View ===== #
@extend_schema(tags=["Cart"])
class CartItemUpdateView(GenericAPIView):
    """
    PATCH /api/v1/cart/items/{item_id}/
    ویرایش آیتم سبد خرید.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemUpdateSerializer

    @extend_schema(
        summary="ویرایش آیتم (تعداد یا آپشن‌ها)",
        description="""
        هر فیلدی که ارسال شود، جایگزین مقدار قبلی می‌شود.
        اگر آپشن‌ها تغییر کنند، ممکن است قیمت کاملاً تغییر کند.
        """,
        parameters=[
            OpenApiParameter("item_id", OpenApiTypes.INT, OpenApiParameter.PATH, description="شناسه آیتم")
        ],
        examples=[
            OpenApiExample(
                'Update Quantity',
                summary='فقط تغییر تعداد',
                value={"quantity": 2000}
            ),
            OpenApiExample(
                'Update Quantity Package',
                summary='تغییر بسته تیراژ',
                value={"quantity_id": 51}
            ),
            OpenApiExample(
                'Update Options',
                summary='تغییر آپشن (تغییر روکش)',
                value={
                    "quantity_id": 50,
                    "options": {
                        "10": 101, 
                        "12": 206
                    }
                }
            )
        ]
    )
    def patch(self, request, item_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # ===== فراخوانی سرویس ===== #
            service = CartItemUpdateService(user=request.user)
            # ===== اجرای سرویس ===== #
            updated_item = service.update(
                cart_item_id=item_id,
                raw_data=serializer.validated_data
            )
            # ===== بازگشت ===== #
            return Response(
                CartItemSerializer(updated_item, context={'request': request}).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
