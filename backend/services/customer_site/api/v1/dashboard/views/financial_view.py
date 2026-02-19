from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample

from core.financial.services import QuotationService, InvoiceService
from ..serializers import (
    QuotationSerializer, QuotationStatusSerializer,
    InvoiceSerializer, InvoiceStatusSerializer
)

# ========== QUOTATION VIEWSET ========== #
@extend_schema(tags=["Dashboard - Quotation"])
class QuotationViewSet(viewsets.ViewSet):
    """
    مجموعه APIهای مدیریت پیش‌فاکتور (Quotation)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = QuotationService()

    # ===== 1. ایجاد پیش‌فاکتور ===== #
    @extend_schema(
        summary="ایجاد پیش‌فاکتور جدید",
        description="ایجاد یک پیش‌فاکتور برای سفارش. تمامی فیلدهای قابل ارسال در مثال زیر آورده شده‌اند. ارسال `order_id` الزامی است.",
        request=QuotationSerializer,
        examples=[
            OpenApiExample(
                name="مثال کامل ایجاد پیش‌فاکتور",
                value={
                    "order_id": 15,
                    "customer_name": "شرکت توسعه و نوآوری سینا",
                    "product_name": "چاپ کاتالوگ 20 صفحه‌ای A4",
                    "product_snapshot": {
                        "material": "گلاسه 150 گرم",
                        "size": "A4",
                        "cover": "سلفون مات"
                    },
                    "quantity": 1000,
                    "estimated_delivery_date": "2026-05-20",
                    "total_price": 45000000,
                    "valid_until": "2026-04-20"
                },
                request_only=True
            )
        ]
    )
    def create(self, request):
        order_id = request.data.get('order_id')
        serializer = QuotationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quotation = self.service.create_quotation(order_id, serializer.validated_data, request.user)
        return Response(QuotationSerializer(quotation).data, status=status.HTTP_201_CREATED)

    # ===== 2. دریافت براساس سفارش ===== #
    @extend_schema(summary="دریافت پیش‌فاکتور براساس ID سفارش")
    @action(detail=False, methods=['get'], url_path='by-order/(?P<order_id>\d+)')
    def get_by_order(self, request, order_id=None):
        quotation = self.service.get_by_order(order_id)
        return Response(QuotationSerializer(quotation).data, status=status.HTTP_200_OK)

    # ===== 3. ویرایش ===== #
    @extend_schema(
        summary="ویرایش پیش‌فاکتور",
        description="ارسال فیلدهایی که نیاز به تغییر دارند. می‌توانید یک یا چند فیلد از مثال زیر را ارسال کنید.",
        request=QuotationSerializer,
        examples=[
            OpenApiExample(
                name="مثال کامل ویرایش فیلدها",
                value={
                    "customer_name": "نام جدید مشتری",
                    "product_name": "تغییر نام محصول",
                    "product_snapshot": {
                        "material": "گلاسه 200 گرم"
                    },
                    "quantity": 1500,
                    "estimated_delivery_date": "2026-06-01",
                    "total_price": 50000000,
                    "valid_until": "2026-05-01"
                },
                request_only=True
            )
        ]
    )
    def partial_update(self, request, pk=None):
        serializer = QuotationSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        quotation = self.service.update_quotation(pk, serializer.validated_data)
        return Response(QuotationSerializer(quotation).data, status=status.HTTP_200_OK)

    # ===== 4. حذف ===== #
    @extend_schema(summary="حذف پیش‌فاکتور")
    def destroy(self, request, pk=None):
        self.service.delete_quotation(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== 5. تایید پیش‌فاکتور ===== #
    @extend_schema(
        summary="تایید (Approve) پیش‌فاکتور",
        description="با فراخوانی این API وضعیت پیش‌فاکتور خودکار به `accepted` تغییر می‌کند. نیازی به بادی نیست."
    )
    @action(detail=True, methods=['patch'], url_path='approve')
    def approve(self, request, pk=None):
        quotation = self.service.approve_quotation(pk)
        return Response(QuotationStatusSerializer(quotation).data, status=status.HTTP_200_OK)

    # ===== 6. تغییر وضعیت ===== #
    @extend_schema(
        summary="تغییر وضعیت پیش‌فاکتور به صورت دستی",
        description="""
**وضعیت‌های مجاز برای ارسال:**
* `draft` : پیش‌نویس
* `sent` : ارسال شده
* `accepted` : تایید شده
* `rejected` : رد شده
* `expired` : منقضی شده
* `converted` : تبدیل شده به سفارش
        """,
        request=QuotationStatusSerializer,
        examples=[
            OpenApiExample(
                name="مثال تغییر وضعیت",
                value={"status": "sent"},
                request_only=True
            )
        ]
    )
    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        serializer = QuotationStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quotation = self.service.change_status(pk, serializer.validated_data.get('status'))
        return Response(QuotationStatusSerializer(quotation).data, status=status.HTTP_200_OK)


# ========== INVOICE VIEWSET ========== #
@extend_schema(tags=["Dashboard - Invoice"])
class InvoiceViewSet(viewsets.ViewSet):
    """
    مجموعه APIهای مدیریت فاکتور (Invoice)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = InvoiceService()

    # ===== 1. ایجاد فاکتور ===== #
    @extend_schema(
        summary="ایجاد فاکتور جدید",
        description="تمامی فیلدهای مالی و توضیحاتی قابل ارسال در این بدنه پشتیبانی می‌شوند.",
        request=InvoiceSerializer,
        examples=[
            OpenApiExample(
                name="مثال کامل ایجاد فاکتور",
                value={
                    "order_id": 22,
                    "paid_amount": 5000000,
                    "items_amount": 10000000,
                    "services_amount": 500000,
                    "tax_amount": 900000,
                    "discount_amount": 0,
                    "final_amount": 11400000,
                    "description": "فاکتور بابت چاپ بنر تبلیغاتی شرکت",
                    "due_date": "2026-08-15T14:30:00Z",
                    "status": "PENDING"
                },
                request_only=True
            )
        ]
    )
    def create(self, request):
        order_id = request.data.get('order_id')
        serializer = InvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invoice = self.service.create_invoice(order_id, serializer.validated_data)
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)

    # ===== 2. دریافت براساس سفارش ===== #
    @extend_schema(summary="دریافت فاکتور براساس ID سفارش")
    @action(detail=False, methods=['get'], url_path='by-order/(?P<order_id>\d+)')
    def get_by_order(self, request, order_id=None):
        invoice = self.service.get_by_order(order_id)
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_200_OK)

    # ===== 3. ویرایش ===== #
    @extend_schema(
        summary="ویرایش فاکتور",
        description="ارسال هر کدام از فیلدهای زیر اختیاری است و فقط فیلد ارسال‌شده آپدیت می‌شود.",
        request=InvoiceSerializer,
        examples=[
            OpenApiExample(
                name="مثال کامل ویرایش فیلدها",
                value={
                    "paid_amount": 11400000,
                    "items_amount": 10000000,
                    "services_amount": 500000,
                    "tax_amount": 900000,
                    "discount_amount": 200000,
                    "final_amount": 11200000,
                    "description": "تسویه کامل انجام شد.",
                    "due_date": "2026-08-20T10:00:00Z",
                    "status": "PAID_FULL"
                },
                request_only=True
            )
        ]
    )
    def partial_update(self, request, pk=None):
        serializer = InvoiceSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        invoice = self.service.update_invoice(pk, serializer.validated_data)
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_200_OK)

    # ===== 4. حذف ===== #
    @extend_schema(summary="حذف فاکتور")
    def destroy(self, request, pk=None):
        self.service.delete_invoice(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== 5. تایید فاکتور ===== #
    @extend_schema(
        summary="نهایی‌سازی (Finalize) فاکتور",
        description="وضعیت به صورت خودکار `FINALIZE` می‌شود و فیلد تاریخ تایید (`finalized_at`) زمان می‌خورد."
    )
    @action(detail=True, methods=['patch'], url_path='approve')
    def approve(self, request, pk=None):
        invoice = self.service.approve_invoice(pk)
        return Response(InvoiceStatusSerializer(invoice).data, status=status.HTTP_200_OK)

    # ===== 6. تغییر وضعیت ===== #
    @extend_schema(
        summary="تغییر وضعیت فاکتور به صورت دستی",
        description="""
        **وضعیت‌های مجاز برای ارسال:**
        * `PENDING` : در انتظار پرداخت
        * `PAID_PARTIAL` : پرداخت ناقص
        * `PAID_FULL` : تسویه کامل
        * `CANCELED` : لغو شده
        * `FINALIZE` : نهایی شده / بسته شده
        """,
        request=InvoiceStatusSerializer,
        examples=[
            OpenApiExample(
                name="مثال پرداخت ناقص",
                value={"status": "PAID_PARTIAL"},
                request_only=True
            ),
            OpenApiExample(
                name="مثال تسویه کامل",
                value={"status": "PAID_FULL"},
                request_only=True
            )
        ]
    )
    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        serializer = InvoiceStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invoice = self.service.change_status(pk, serializer.validated_data.get('status'))
        return Response(InvoiceStatusSerializer(invoice).data, status=status.HTTP_200_OK)
