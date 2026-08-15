from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample

from core.financial.services import InvoiceService
from ..serializers import InvoiceSerializer, InvoiceStatusSerializer


@extend_schema(tags=["Dashboard - Invoice"])
class InvoiceViewSet(viewsets.ViewSet):
    """
    مدیریت فاکتورها
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = InvoiceService()

    # ===== ۱. لیست فاکتورها ===== #
    @extend_schema(summary="لیست تمام فاکتورها", responses=InvoiceSerializer(many=True))
    def list(self, request):
        invoices = self.service.list_invoices()
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    # ===== ۲. جزئیات فاکتور با شناسه ===== #
    @extend_schema(summary="جزئیات فاکتور", responses=InvoiceSerializer)
    def retrieve(self, request, pk=None):
        invoice = self.service.get_invoice(pk)
        return Response(InvoiceSerializer(invoice).data)

    # ===== ۳. دریافت فاکتور بر اساس سفارش ===== #
    @extend_schema(
        summary="دریافت فاکتور بر اساس شناسه سفارش",
        description="با ارسال order_id فاکتور مرتبط بازگردانده می‌شود.",
        responses=InvoiceSerializer,
    )
    @action(detail=False, methods=['get'], url_path='by-order/(?P<order_id>\d+)')
    def by_order(self, request, order_id=None):
        invoice = self.service.get_by_order(int(order_id))
        return Response(InvoiceSerializer(invoice).data)

    # ===== ۴. ایجاد فاکتور دستی ===== #
    @extend_schema(
        summary="ایجاد فاکتور جدید",
        description="ایجاد فاکتور برای سفارش. مقدار paid_amount و final_amount را ارسال کنید. وضعیت فاکتور به‌صورت خودکار تعیین می‌شود.",
        request=InvoiceSerializer,
        responses={201: InvoiceSerializer},
        examples=[
            OpenApiExample(
                "مثال ایجاد فاکتور",
                value={
                    "order": 22,  # یا order_id
                    "paid_amount": 5000000,
                    "items_amount": 10000000,
                    "services_amount": 500000,
                    "tax_amount": 900000,
                    "discount_amount": 0,
                    "final_amount": 11400000,
                    "description": "فاکتور بابت چاپ بنر",
                    "due_date": "2026-08-15",
                },
                request_only=True,
            )
        ],
    )
    def create(self, request):
        serializer = InvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = self.service.create_invoice(serializer.validated_data, request.user)
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)

    # ===== ۵. ویرایش فاکتور ===== #
    @extend_schema(
        summary="ویرایش فاکتور",
        description="فقط فیلدهای ارسالی تغییر می‌کنند و لاگ مالی ثبت می‌شود.",
        request=InvoiceSerializer,
        responses={200: InvoiceSerializer},
    )
    def partial_update(self, request, pk=None):
        serializer = InvoiceSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        invoice = self.service.update_invoice(pk, serializer.validated_data, request.user)
        return Response(InvoiceSerializer(invoice).data)

    # ===== ۶. حذف فاکتور ===== #
    @extend_schema(summary="حذف فاکتور")
    def destroy(self, request, pk=None):
        self.service.delete_invoice(pk, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== ۷. نهایی‌سازی فاکتور ===== #
    @extend_schema(
        summary="نهایی‌سازی فاکتور",
        description="وضعیت فاکتور به FINALIZE تغییر می‌کند و تاریخ نهایی‌سازی ثبت می‌شود.",
    )
    @action(detail=True, methods=['patch'], url_path='finalize')
    def finalize(self, request, pk=None):
        invoice = self.service.finalize_invoice(pk, request.user)
        return Response(InvoiceStatusSerializer(invoice).data)

    # ===== ۸. تغییر وضعیت دستی ===== #
    @extend_schema(
        summary="تغییر وضعیت فاکتور",
        description="وضعیت مجاز: PENDING, PAID_PARTIAL, PAID_FULL, CANCELED, FINALIZE",
        request=InvoiceStatusSerializer,
        responses={200: InvoiceStatusSerializer},
    )
    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        serializer = InvoiceStatusSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data.get('status')
        invoice = self.service.change_status(pk, new_status, request.user)
        return Response(InvoiceStatusSerializer(invoice).data)