from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiTypes

from apps.order.services import CreateOrderFromCartService
from apps.order.exceptions import (
    EmptyCartError,
    InsufficientFundsError,
    OrderCreationError
)
from .serializers import OrderSerializer

# ========== Create Order View ========== #
@extend_schema(tags=["Order"])
class CreateOrderView(GenericAPIView):
    """
    POST /api/v1/orders/checkout/
    Converts the user's cart into a final order.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer


    @extend_schema(
        summary="ثبت سفارش نهایی",
        description="""
        این متد یک آیتم خاص از سبد خرید (که احتمالاً فایل‌هایش آپلود شده) را می‌گیرد و تبدیل به سفارش می‌کند.
        
        **مراحل:**
        1. اعتبارسنجی آدرس و نوع سفارش.
        2. بررسی موجودی کیف پول (اگر پرداخت آنی باشد).
        3. کسر از کیف پول و ایجاد سفارش.
        4. بازگرداندن اطلاعات کامل سفارش ایجاد شده برای نمایش فاکتور.
        """,
        parameters=[
            OpenApiParameter(
                name='item_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='شناسه آیتم موجود در سبد خرید (Cart Item ID)',
                required=True
            )
        ],
        request=OrderSerializer,
        responses={
            201: OrderSerializer,
            400: OpenApiTypes.OBJECT,
            402: OpenApiTypes.OBJECT
        },
        examples=[
            # ===== مثال درخواست ===== #
            OpenApiExample(
                'Checkout Request',
                summary='درخواست ثبت سفارش',
                description='ارسال شناسه آدرس و نوع سفارش.',
                value={
                    "address_id": 15,
                    "type": "2" 
                },
                request_only=True
            ),
            # ===== مثال پاسخ موفق ===== #
            OpenApiExample(
                'Order Created Response',
                summary='پاسخ موفق (فاکتور)',
                description='خروجی شامل جزئیات فنی (Specs) برای نمایش به کاربر است.',
                value={
                    "id": 2055,
                    "order_code": "ORD-1402-859",
                    "user": "ali_rezaei",
                    "status": "آغازین",
                    "type_display": "سفارش اختصاصی",
                    "total_price": "2500000",
                    "address": "تهران، خیابان آزادی...",
                    "created_at": "2024-03-15T10:00:00Z",
                    "item_detail": {
                        "id": 501,
                        "product_name": "کارت ویزیت لمینت مات",
                        "quantity": 1000,
                        "price": "2500000",
                        "specs": {
                            "dimensions": "9 x 6 cm",
                            "has_design": True,
                            "options": [
                                {
                                    "id": 10,
                                    "option_name": "نوع کاغذ",
                                    "value_label": "گلاسه ۳۰۰ گرم",
                                    "price_impact": 500000.0
                                },
                                {
                                    "id": 12,
                                    "option_name": "گوشه",
                                    "value_label": "گرد",
                                    "price_impact": 100000.0
                                }
                            ],
                            "breakdown_present": True
                        },
                        "design_files": [
                            {
                                "id": 88,
                                "requirement_name": "طرح رو",
                                "file_url": "https://api.printoo.ir/media/..."
                            }
                        ]
                    }
                },
                response_only=True,
                status_codes=[201]
            ),
            # ===== مثال خطای موجودی ===== #
            OpenApiExample(
                'Insufficient Funds',
                summary='خطای کمبود موجودی (402)',
                value={"error": "موجودی کیف پول کافی نیست. لطفاً حساب خود را شارژ کنید."},
                response_only=True,
                status_codes=[402]
            )
        ]
    )
    def post(self, request, item_id, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address_instance = serializer.validated_data.get('address')
        order_type = request.data.get('type', '2')

        try:
            service = CreateOrderFromCartService()
            
            # ===== اجرای سرویس ===== #
            created_order = service.execute(
                user=request.user, 
                address=address_instance,
                order_type=order_type,
                cart_item_id=item_id
            )
            
            # ===== نمایش خروجی ===== #
            output_serializer = self.get_serializer(
                created_order, 
                many=False,
                context={'request': request}
            )
            
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        except EmptyCartError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except InsufficientFundsError as e:
            return Response({"error": str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED)
            
        except Exception as e:
            return Response(
                {"error": "An error occurred while placing the order.", "detail": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
