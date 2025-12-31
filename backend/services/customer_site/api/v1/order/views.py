from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiTypes

from apps.order.services import CreateOrderFromCartService
from apps.order.exceptions import EmptyCartError, InsufficientFundsError
from .serializers import OrderSerializer

# ========================================== #
# ===== 1. Single Item Checkout View ======= #
# ========================================== #
@extend_schema(tags=["Order"])
class CreateOrderView(GenericAPIView):
    """
    تبدیل یک آیتم خاص سبد خرید به سفارش نهایی.
    """
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer

    @extend_schema(
        summary="ثبت سفارش نهایی (تکی)",
        description="""
        این متد برای نهایی کردن خرید یک آیتم خاص استفاده می‌شود.
        
        **نکات مهم برای فرانت‌‌اند:**
        1. **کاربر مهمان (Guest):** ارسال `first_name`, `last_name`, `phone_number` و تمام فیلدهای آدرس (`province_id`, `city_id`, `address_text`) **اجباری** است.
        2. **کاربر لاگین شده (Auth):**
            * حالت الف) انتخاب از لیست آدرس‌ها: فقط `address_id` ارسال شود.
            * حالت ب) ثبت آدرس جدید: فیلدهای آدرس (`province_id`, ...) ارسال شود (address_id نال باشد).
        3. **نوع سفارش:** برای مهمان به صورت خودکار روی حالت **اختصاصی (2)** تنظیم می‌شود.
        """,
        parameters=[
            OpenApiParameter(
                name='item_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='شناسه آیتم سبد خرید (CartItem ID) که باید تبدیل به سفارش شود.',
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
            # ===== EXAMPLE 1: GUEST USER ===== #
            OpenApiExample(
                'Scenario: Guest User (Full Info)',
                summary='سناریو ۱: کاربر مهمان (Guest)',
                description='کاربر لاگین نکرده است، پس باید تمام مشخصات هویتی و آدرس را دستی وارد کند.',
                value={
                    "type": "2",
                    "first_name": "امیر",
                    "last_name": "رضایی",
                    "phone_number": "09121234567",
                    "company_name": "شرکت چاپ نمونه",
                    "province_id": 8,
                    "city_id": 124,
                    "address_text": "خیابان آزادی، کوچه مهر، پلاک ۱۰، واحد ۴",
                    "postal_code": "1234567890"
                },
                request_only=True
            ),
            # ===== EXAMPLE 2: AUTH USER (SAVED ADDRESS) ===== #
            OpenApiExample(
                'Scenario: Auth User (Saved Address)',
                summary='سناریو ۲: کاربر عضو (آدرس ذخیره شده)',
                description='کاربر لاگین است و یکی از آدرس‌های پروفایل خود را (address_id) انتخاب کرده است.',
                value={
                    "type": "1",
                    "address_id": 15
                },
                request_only=True
            ),
            # ===== EXAMPLE 3: AUTH USER (NEW ADDRESS) ===== #
            OpenApiExample(
                'Scenario: Auth User (New Address)',
                summary='سناریو ۳: کاربر عضو (آدرس جدید)',
                description='کاربر لاگین است اما می‌خواهد سفارش به آدرس جدیدی ارسال شود (همزمان پروفایل هم آپدیت می‌شود).',
                value={
                    "type": "1",
                    "first_name": "امیر",
                    "last_name": "رضایی",
                    "phone_number": "09129998877",
                    "province_id": 5,
                    "city_id": 40,
                    "address_text": "اصفهان، میدان نقش جهان...",
                    "postal_code": "8181818181"
                },
                request_only=True
            ),
            # ===== EXAMPLE 4: SUCCESS RESPONSE ===== #
            OpenApiExample(
                'Success Response (Invoice)',
                summary='پاسخ موفق (فاکتور نهایی)',
                description='خروجی سفارش ثبت شده شامل وضعیت، قیمت نهایی و جزئیات فنی محصول.',
                value={
                    "id": 2055,
                    "order_code": "ORD-859123",
                    "status": "در انتظار بررسی",
                    "type_display": "سفارش اختصاصی",
                    "total_price": "2500000",
                    "recipient_name": "امیر رضایی",
                    "recipient_phone": "09121234567",
                    "full_address": "تهران - تهران - خیابان آزادی، کوچه مهر، پلاک ۱۰ - کدپستی: 1234567890",
                    "created_at": "2024-03-20T14:30:00Z",
                    "item_detail": {
                        "id": 501,
                        "product_name": "کارت ویزیت لمینت مات",
                        "quantity": 1000,
                        "price": "2500000",
                        "specs": {
                            "dimensions": "9 x 6 cm",
                            "has_design": True,
                            "options": [
                                {"option_name": "گوشه", "value_label": "گرد", "price_impact": 100000},
                                {"option_name": "جنس کاغذ", "value_label": "ایندربرد ۳۰۰ گرم", "price_impact": 0}
                            ]
                        },
                        "design_files": [
                            {
                                "id": 88,
                                "requirement_name": "فایل چاپی (PDF)",
                                "file_url": "https://api.printoo.ir/media/orders/..."
                            }
                        ]
                    }
                },
                response_only=True,
                status_codes=[201]
            ),
        ]
    )
    def post(self, request, item_id, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        
        checkout_data = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'phone_number': data.get('phone_number'),
            'company_name': data.get('company_name'),
            'address_id': data.get('address_id'),
            'province_id': data.get('province_id'),
            'province_name': data.get('province_name'),
            'city_id': data.get('city_id'),
            'city_name': data.get('city_name'),
            'address_text': data.get('address_text'),
            'postal_code': data.get('postal_code'),
        }

        order_type = data.get('type', '1')
        # ===== تشخیص کاربر ===== #
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key

        try:
            service = CreateOrderFromCartService()
            created_order = service.execute(
                checkout_data=checkout_data,
                cart_item_id=item_id,
                user=user,
                session_key=session_key,
            )
            output_serializer = self.get_serializer(created_order)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        except (EmptyCartError, ValueError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except InsufficientFundsError as e:
            return Response({"error": str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED)
        except Exception as e:
            return Response({"error": "System Error", "detail": str(e)}, status=500)


# ========================================== #
# ===== 2. Bulk Checkout View ============== #
# ========================================== #
@extend_schema(tags=["Order"])
class BulkCreateOrderView(GenericAPIView):
    """
    تسویه حساب گروهی (کل سبد خرید).
    """
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer
    
    @extend_schema(
        summary="ثبت سفارش گروهی (Bulk Checkout)",
        description="تمام آیتم‌های سبد خرید را تبدیل به سفارش‌های مجزا می‌کند اما با یک تراکنش مالی واحد.",
        request=OrderSerializer,
        responses={201: OrderSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Bulk Request (Guest)',
                summary='درخواست گروهی (مهمان)',
                value={
                    "type": "2",
                    "first_name": "سارا",
                    "last_name": "محمدی",
                    "phone_number": "0935...",
                    "province_id": 1,
                    "city_id": 2,
                    "address_text": "خیابان ولیعصر...",
                    "postal_code": "1111111111"
                },
                request_only=True
            ),
            OpenApiExample(
                'Bulk Response',
                summary='پاسخ موفق (لیست سفارشات)',
                value=[
                    {
                        "id": 2055,
                        "order_code": "ORD-101",
                        "status": "در انتظار بررسی",
                        "total_price": "100000",
                        "full_address": "تهران - تهران - خیابان ولیعصر...",
                        "item_detail": {"product_name": "تراکت A5", "quantity": 2000}
                    },
                    {
                        "id": 2056,
                        "order_code": "ORD-102",
                        "status": "در انتظار بررسی",
                        "total_price": "500000",
                        "full_address": "تهران - تهران - خیابان ولیعصر...",
                        "item_detail": {"product_name": "کارت ویزیت", "quantity": 1000}
                    }
                ],
                response_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # ===== آماده سازی اطلاعات ===== #
        checkout_data = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'phone_number': data.get('phone_number'),
            'company_name': data.get('company_name'),
            'address_id': data.get('address_id'),
            'province_id': data.get('province_id'),
            'province_name': data.get('province_name'),
            'city_id': data.get('city_id'),
            'city_name': data.get('city_name'),
            'address_text': data.get('address_text'),
            'postal_code': data.get('postal_code'),
        }

        order_type = data.get('type', '1')
        # ===== تشخیص کاربر ===== #
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key

        try:
            service = CreateOrderFromCartService()
            created_orders = service.execute_bulk(
                checkout_data=checkout_data,
                user=user,
                session_key=session_key,
                order_type=order_type
            )
            output_serializer = self.get_serializer(created_orders, many=True)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        except (EmptyCartError, ValueError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except InsufficientFundsError as e:
            return Response({"error": str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED)
        except Exception as e:
            return Response({"error": "System Error", "detail": str(e)}, status=500)
