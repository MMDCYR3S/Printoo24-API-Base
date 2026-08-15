from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from core.financial.services import PaymentService
from django.core.exceptions import ValidationError

from apps.dashboard.services.order_service import OrderDashboardService
from ..serializers.order_serializers import (
    OrderDetailSerializer, OrderCreateSerializer, OrderUpdateSerializer,
    ChangeStatusSerializer, BulkActionIdsSerializer, BulkChangeStatusSerializer,
    OrderStatusSerializer, UserAddressSerializer, OrderItemUploadSerializer,
    CustomerListSerializer, OrderFinancialSerializer,
    PaymentSerializer, PaymentRegisterSerializer, PaymentRejectSerializer,
)
from apps.dashboard.tasks import upload_order_item_file_task
from rest_framework import parsers

@extend_schema(tags=["Admin - Order Management"])
class OrderDashboardViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OrderDashboardService()
        self.payment_service = PaymentService()

    # ===== LIST ===== #
    @extend_schema(summary="لیست سفارشات", responses=OrderDetailSerializer(many=True))
    def list(self, request):
        queryset = self.service.get_order_list()
        serializer = OrderDetailSerializer(queryset, many=True)
        return Response(serializer.data)

    # ===== RETRIEVE ===== #
    @extend_schema(summary="جزئیات سفارش", responses=OrderDetailSerializer)
    def retrieve(self, request, pk=None):
        try:
            order = self.service.get_order_detail(pk)
            return Response(OrderDetailSerializer(order).data)
        except Exception:
            return Response({'detail': 'یافت نشد'}, status=status.HTTP_404_NOT_FOUND)

    # ===== CREATE ===== #
    @extend_schema(
        summary="ایجاد سفارش دستی (تک آیتمی)",
        description="""شما فقط اطلاعات سفارش و product_id را می‌فرستید. سیستم خودش آیتم را می‌سازد.""",
        request=OrderCreateSerializer,
        responses={201: OrderDetailSerializer},
        examples=[
            OpenApiExample(
                "کاربر ثبت‌نام‌شده (با آدرس ذخیره‌شده)",
                value={
                    "user_id": 10,
                    "address_id": 5,
                    "company_name": "چاپخانه نمونه",
                    "type": "1",
                    "product_id": 49,
                    "has_design": True,
                    "selected_options": [
                        {"field_id": 13, "choice_id": 24},
                        {"field_id": 14, "choice_id": 27}
                    ]
                },
                request_only=True
            ),
            OpenApiExample(
                "مهمان (بدون حساب کاربری)",
                value={
                    "recipient_name": "علی حسینی",
                    "recipient_phone": "09137555555",
                    "full_address": "اصفهان - خیابان بزرگمهر - پلاک ۱۲",
                    "company_name": "شرکت نمونه",
                    "type": "1",
                    "product_id": 49,
                    "has_design": False,
                    "selected_options": [
                        {"field_id": 13, "choice_id": 24}
                    ]
                },
                request_only=True
            ),
        ]
    )
    def create(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = self.service.create_order(serializer.validated_data)
            return Response(OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== UPDATE DETAILS ===== #
    @extend_schema(
        summary="ویرایش مشخصات یا محصول سفارش",
        description="""
        تمام فیلدها اختیاری هستند و فقط آنچه ارسال شود آپدیت می‌شود.

        **منطق قیمت:**
        - `total_price_override` ارسال شد → قیمت دستی، محاسبه انجام نمی‌شود
        - `total_price_override` نبود ولی `product_id` یا `selected_options` بود → محاسبه خودکار
        """,
        request=OrderUpdateSerializer,
        responses={200: OrderDetailSerializer},
        examples=[
            OpenApiExample(
                "فقط ویرایش اطلاعات گیرنده",
                value={
                    "recipient_name": "رضا احمدی",
                    "recipient_phone": "09120000000",
                    "company_name": "شرکت نمونه"
                },
                request_only=True
            ),
            OpenApiExample(
                "ویرایش آدرس سیستمی",
                value={
                    "address_id": 7
                },
                request_only=True
            ),
            OpenApiExample(
                "تغییر محصول و آپشن‌ها — قیمت خودکار",
                value={
                    "product_id": 50,
                    "quantity": 2,
                    "selected_options": [
                        {"field_id": 13, "choice_id": 25},
                        {"field_id": 14, "choice_ids": [3, 5]},
                        {"field_id": 15, "value": "A4"}
                    ]
                },
                request_only=True
            ),
            OpenApiExample(
                "ست کردن قیمت دستی — بدون محاسبه مجدد",
                value={
                    "total_price_override": 850000
                },
                request_only=True
            ),
            OpenApiExample(
                "تغییر آپشن‌ها + قیمت دستی — قیمت دستی اولویت دارد",
                value={
                    "product_id": 50,
                    "selected_options": [
                        {"field_id": 13, "choice_id": 26}
                    ],
                    "total_price_override": 950000
                },
                request_only=True
            ),
        ]
    )
    def partial_update(self, request, pk=None):
        serializer = OrderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = self.service.update_order(pk, serializer.validated_data)
            return Response(OrderDetailSerializer(order).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== DELETE ===== #
    @extend_schema(summary="حذف سفارش تکی")
    def destroy(self, request, pk=None):
        try:
            self.service.delete_order(pk)
            return Response({"detail": "با موفقیت حذف شد."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== CHANGE STATUS (SINGLE) ===== #
    @extend_schema(
        summary="تغییر وضعیت سفارش تکی", 
        request=ChangeStatusSerializer,
        examples=[
            OpenApiExample(
                "تغییر وضعیت با internal_code",
                value={
                    "internal_code": "PENDING_INITIAL_ADMIN",
                    "description": "وضعیت به انتظار بررسی برگشت"
                },
                request_only=True
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        serializer = ChangeStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            data = serializer.validated_data
            order = self.service.change_status(pk, data['status_code'], request.user, data.get('description', ''))
            return Response(OrderDetailSerializer(order).data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== BULK DELETE ===== #
    @extend_schema(summary="حذف گروهی سفارشات", request=BulkActionIdsSerializer)
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        serializer = BulkActionIdsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.service.bulk_delete(serializer.validated_data['order_ids'])
        return Response(result)

    # ===== BULK CHANGE STATUS ===== #
    @extend_schema(
        summary="تغییر وضعیت گروهی سفارشات", 
        request=BulkChangeStatusSerializer,
        examples=[
            OpenApiExample(
                "تغییر گروهی با internal_code",
                value={
                    "order_ids": [91, 92, 93],
                    "internal_code": "APPROVED_ADMIN"
                },
                request_only=True
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='bulk-change-status')
    def bulk_change_status(self, request):
        serializer = BulkChangeStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            updated = self.service.bulk_change_status(data['order_ids'], data['internal_code'], request.user)
            return Response({"detail": f"وضعیت {updated} سفارش با موفقیت تغییر کرد."})
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="لیست وضعیت‌های سفارش", 
        description="فرانت‌اند با این API لیست وضعیت‌ها را می‌گیرد تا در دراپ‌داون‌ها به کاربر نمایش دهد و `internal_code` را برای سرور بفرستد.",
        responses=OrderStatusSerializer(many=True)
    )
    @action(detail=False, methods=['get'], url_path='statuses')
    def statuses(self, request):
        statuses = self.service.get_order_statuses()
        serializer = OrderStatusSerializer(statuses, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="لیست آدرس‌های یک کاربر",
        responses=UserAddressSerializer(many=True),
        parameters=[OpenApiParameter('user_id', int, OpenApiParameter.QUERY, required=True)]
    )
    @action(detail=False, methods=['get'], url_path='user-addresses')
    def user_addresses(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'detail': 'user_id الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)
        addresses = self.service.get_user_addresses(user_id)
        return Response(UserAddressSerializer(addresses, many=True).data)

    # ===== لیست مشتریان برای سفارش دستی ===== #
    @extend_schema(
        summary="لیست مشتریان برای سفارش دستی",
        description="دریافت لیست تمام مشتریانی که ادمین نیستند، برای انتخاب در هنگام ثبت سفارش دستی",
        responses=CustomerListSerializer(many=True)
    )
    @action(detail=False, methods=['get'], url_path='customers')
    def customers(self, request):
        customers = self.service.get_all_customers()
        return Response(CustomerListSerializer(customers, many=True).data)

    # ===== ORDER ITEM FILE UPLOAD ===== #
    @extend_schema(
        summary="آپلود فایل طراحی برای یک آیتم سفارش",
        request=OrderItemUploadSerializer,
        responses={202: {"description": "آپلود در صف قرار گرفت"}},
    )
    @action(detail=False, methods=['post'], url_path=r'items/(?P<item_id>\d+)/upload-file',
            parser_classes=[parsers.MultiPartParser])
    def upload_item_file(self, request, item_id=None):
        serializer = OrderItemUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.service.upload_order_item_file(int(item_id), serializer.validated_data['file'])
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response({'detail': 'فایل در صف آپلود قرار گرفت.'}, status=status.HTTP_202_ACCEPTED)

    @extend_schema(summary="حذف فایل‌های طراحی یک آیتم سفارش")
    @action(detail=False, methods=['delete'], url_path=r'items/(?P<item_id>\d+)/delete-file')
    def delete_item_file(self, request, item_id=None):
        try:
            self.service.delete_order_item_file(int(item_id))
            return Response({'detail': 'فایل با موفقیت حذف شد.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ===== FINANCIAL ORDER FIELDS (فقط نمایش) ===== #
    @extend_schema(
        tags=["Admin - Order Management"],
        summary="مشاهده اطلاعات مالی سفارش",
        description="""نمایش جدأ مالی سفارش.
        قانون: تغییر قیمت سفارش به‌صورت مستقیم مجاز نیست؛ قیمتِ اصلی و آیتم از طریق
        پیش‌فاکتور و قیمت‌های نهایی/جانبی از طریق فاکتور اعمال می‌شود.""",
        responses={200: OrderFinancialSerializer},
    )
    @action(detail=True, methods=['get'], url_path='financial')
    def financial(self, request, pk=None):
        try:
            order = self.service.get_order_detail(pk)
        except Exception:
            return Response({'detail': 'سفارش یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderFinancialSerializer(order).data)

    # ===== PAYMENTS (LIST / REGISTER) =====
    @extend_schema(
        tags=["Admin - Order Management"],
        summary="لیست پرداخت‌های سفارش",
        responses=PaymentSerializer(many=True),
    )
    @action(detail=True, methods=['get'], url_path='payments')
    def payments(self, request, pk=None):
        try:
            order = self.service.get_order_detail(pk)
        except Exception:
            return Response({'detail': 'سفارش یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PaymentSerializer(order.payments.all(), many=True).data)

    @extend_schema(
        tags=["Admin - Order Management"],
        summary="ثبت پرداخت دستی/آنلاین برای سفارش",
        description="پرداخت با وضعیت در انتظار تایید ثبت میشود؛ پس از تایید ادمین روی سفارش اعمال میشود.",
        request=PaymentRegisterSerializer,
        responses={201: PaymentSerializer},
    )
    @action(detail=True, methods=['post'], url_path='payments')
    def register_payment(self, request, pk=None):
        serializer = PaymentRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment = self.payment_service.register_payment(
                order_id=int(pk),
                user=request.user,
                amount=serializer.validated_data['amount'],
                method=serializer.validated_data['method'],
                reference_number=serializer.validated_data.get('reference_number', ''),
                description=serializer.validated_data.get('description', ''),
                created_by=request.user,
            )
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    # ===== PAYMENT APPROVE / REJECT =====
    @extend_schema(
        tags=["Admin - Order Management"],
        summary="تایید پرداخت",
        description="پرداخت تایید میشود و مبلغ آن روی مبالغ و وضعیت مالی سفارش اعمال میشود.",
        responses={200: PaymentSerializer},
    )
    @action(detail=False, methods=['post'], url_path=r'payments/(?P<payment_id>\d+)/approve')
    def approve_payment(self, request, payment_id=None):
        try:
            payment = self.payment_service.approve_payment(int(payment_id), request.user)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PaymentSerializer(payment).data)

    @extend_schema(
        tags=["Admin - Order Management"],
        summary="رد پرداخت",
        description="رد یک پرداخت در انتظار (اختیاری با ذکر دلیل).",
        request=PaymentRejectSerializer,
        responses={200: PaymentSerializer},
    )
    @action(detail=False, methods=['post'], url_path=r'payments/(?P<payment_id>\d+)/reject')
    def reject_payment(self, request, payment_id=None):
        serializer = PaymentRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment = self.payment_service.reject_payment(
                int(payment_id), request.user, serializer.validated_data.get('reason', '')
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PaymentSerializer(payment).data)
