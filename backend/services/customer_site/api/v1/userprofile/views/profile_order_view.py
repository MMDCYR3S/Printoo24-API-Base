from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.userprofile.services import UserOrderListService
from ..serializers import OrderWithDetailsSerializer, OrderSerializer, QuotationSerializer, UserInvoiceSerializer

# ===== User Order List APIView ===== #
@extend_schema(tags=["Profile"])
class UserOrderListAPIView(APIView):
    """
    لیست سابقه سفارشات مشتری (خلاصه).
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service = UserOrderListService()

    @extend_schema(
        summary="لیست سفارشات کاربر (خلاصه)",
        responses={200: OrderSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Orders List',
                value=[
                    {
                        "id": 2050,
                        "user": 15,
                        "recipient_name": "محمد رضایی",
                        "recipient_phone": "09137555555",
                        "status": "در حال چاپ",
                        "type_display": "سفارش معمولی",
                        "total_price": "1500000",
                        "created_at": "2023-11-20T14:00:00Z"
                    }
                ]
            )
        ]
    )
    def get(self, request):
        orders = self._service.get_user_orders(request.user.id)
        
        serializer = OrderSerializer(
            orders, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

# ===== User Order Detail APIView ===== #
@extend_schema(tags=["Profile"])
class UserOrderDetailAPIView(APIView):
    """
    جزئیات کامل سفارش مشتری (شامل فایل‌ها و آیتم‌ها).
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service = UserOrderListService()

    @extend_schema(
        summary="جزئیات کامل سفارش",
        description="خروجی شامل اطلاعات محصول (آبجکت تودرتو)، مشخصات فنی استخراج شده و فایل‌های طراحی است.",
        responses={200: OrderWithDetailsSerializer},
        examples=[
            OpenApiExample(
                'Complex Order Detail',
                value={
                    "id": 2050,
                    "order_code": "4582-PENDING-CARD-2023",
                    "status_display": "تایید شده",
                    "total_price": "2500000",
                    "full_address": "تهران، خیابان آزادی، ...",
                    "created_at": "2023-11-20T14:00:00Z",
                    "order_item": [
                        {
                            "id": 501,
                            "product": {
                                "name": "کارت ویزیت لمینت",
                                "code": "8234-PRINT-CARD-2023",
                                "slug": "laminate-business-card",
                                "image": "https://api.printoo.ir/media/products/card.jpg"
                            },
                            "item_price": "1250000",
                            "quantity": 1000,
                            "specs": {
                                "dimensions": "9 x 5 cm",
                                "material": "گلاسه ۳۰۰ گرم",
                                "options": ["روکش: لمینت براق"]
                            },
                            "design_files": [
                                {
                                    "id": 10,
                                    "requirement_name": "طرح روی کارت",
                                    "file_url": "https://api.printoo.ir/media/designs/v1.pdf"
                                }
                            ]
                        }
                    ]
                }
            )
        ]
    )
    def get(self, request, order_id):
        try:
            order = self._service.get_order_detail(request.user.id, order_id)
            
            # ===== اصلاح حیاتی: ارسال context ===== #
            serializer = OrderWithDetailsSerializer(
                order, 
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        except (ValidationError, NotFound) as e:
            # مدیریت خطای تمیز
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': 'خطایی رخ داد.', 'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@extend_schema(tags=["Profile"])
class UserOrderQuotationAPIView(APIView):
    """
    نمایش پیش‌فاکتور (Quotation) یک سفارش خاص.
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service = UserOrderListService()

    @extend_schema(
        summary="دریافت پیش‌فاکتور سفارش",
        description="این متد اطلاعات پیش‌فاکتور صادر شده در لحظه ثبت سفارش (شامل قیمت قطعی و مشخصات فنی فریز شده) را برمی‌گرداند.",
        responses={200: QuotationSerializer},
        examples=[
            OpenApiExample(
                'Quotation Example',
                value={
                    "id": 101,
                    "quotation_number": "QUOT-A1B2C3D4",
                    "customer_name": "علی علوی",
                    "product_name": "کارت ویزیت",
                    "product_image_url": "http://api.../media/...",
                    "quantity": 1000,
                    "total_price": "1500000.00",
                    "created_at": "2023-12-01T10:00:00Z",
                    "status": "converted",
                    "snapshot_details": {
                        "dimensions": "9 x 6",
                        "material": "گلاسه ۳۰۰ گرم",
                        "features": ["روکش: سلفون مات"]
                    }
                }
            )
        ]
    )
    def get(self, request, order_id):
        try:
            quotation = self._service.get_order_quotation(request.user.id, order_id)
            
            serializer = QuotationSerializer(
                quotation, 
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        except NotFound as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'detail': 'خطایی در دریافت پیش‌فاکتور رخ داد.', 'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@extend_schema(tags=["Profile"])
class UserOrderInvoiceAPIView(APIView):
    """
    نمایش فاکتور یک سفارش خاص (فقط در صورت تسویه کامل).
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service = UserOrderListService()

    @extend_schema(
        summary="دریافت فاکتور سفارش",
        description="این متد فاکتور سفارش را برمی‌گرداند. توجه: فاکتور تنها در صورتی نمایش داده می‌شود که وضعیت آن تسویه کامل (PAID_FULL) یا نهایی شده (FINALIZE) باشد.",
        responses={200: UserInvoiceSerializer},
        examples=[
            OpenApiExample(
                'Invoice Example',
                value={
                    "id": 50,
                    "invoice_number": "INV-4582-PENDING-CARD-2023",
                    "items_amount": 2500000,
                    "services_amount": 0,
                    "tax_amount": 225000,
                    "discount_amount": 0,
                    "final_amount": 2725000,
                    "paid_amount": 2725000,
                    "remaining_amount": 0,
                    "description": "تسویه شده از طریق درگاه پرداخت",
                    "status": "PAID_FULL",
                    "status_display": "تسویه کامل",
                    "issued_at": "2023-11-20T14:00:00Z",
                    "finalized_at": "2023-11-21T10:00:00Z"
                }
            )
        ]
    )
    def get(self, request, order_id):
        try:
            # فراخوانی متد جدیدی که در سرویس نوشتیم
            invoice = self._service.get_order_invoice(request.user.id, order_id)
            
            serializer = UserInvoiceSerializer(invoice)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except NotFound as e:
            # خطای 404 برای زمانی که فاکتور نیست، مال کاربر نیست یا هنوز پرداخت نشده
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'detail': 'خطایی در دریافت فاکتور رخ داد.', 'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
