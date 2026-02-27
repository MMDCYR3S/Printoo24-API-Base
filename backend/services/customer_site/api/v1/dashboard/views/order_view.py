from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.core.exceptions import ValidationError

from apps.dashboard.services.order_service import OrderDashboardService
from ..serializers.order_serializers import (
    OrderDetailSerializer, OrderCreateSerializer, OrderUpdateSerializer,
    ChangeStatusSerializer, BulkActionIdsSerializer, BulkChangeStatusSerializer,
    OrderStatusSerializer
)

@extend_schema(tags=["Admin - Order Management"])
class OrderDashboardViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OrderDashboardService()

    # ===== LIST ===== #
    @extend_schema(summary="لیست سفارشات", responses=OrderDetailSerializer(many=True))
    def list(self, request):
        queryset = self.service.get_order_list()
        # در دنیای واقعی اینجا نیاز به Pagination است. اگر کلاس صفحه بندی دارید اعمال کنید.
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
                "نمونه ثبت سفارش یکپارچه",
                value={
                    "user_id": 10,
                    "recipient_name": "علی حسینی",
                    "recipient_phone": "09137555555",
                    "full_address": "اصفهان - خیابان بزرگمهر",
                    "type": "1",
                    "product_id": 49,
                    "has_design": True,
                    "selected_options": [
                        {"field_id": 13, "choice_id": 24},
                        {"field_id": 14, "choice_id": 27}
                    ]
                },
                request_only=True
            )
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
        description="""شما می‌تونید فقط آدرس رو ادیت کنید، یا اگه نیاز بود کل محصول و آپشن‌هاش رو عوض کنید.""",
        request=OrderUpdateSerializer,
        responses={200: OrderDetailSerializer},
        examples=[
            OpenApiExample(
                "تغییر آپشن‌های محصول در ویرایش",
                value={
                    "recipient_name": "علی حسینی (ادیت شده)",
                    "product_id": 49,
                    "selected_options": [
                        {"field_id": 13, "choice_id": 25}
                    ]
                },
                request_only=True
            )
        ]
    )
    def partial_update(self, request, pk=None):
        serializer = OrderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = self.service.update_order(pk, serializer.validated_data)
            return Response(OrderDetailSerializer(order).data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== DELETE ===== #
    @extend_schema(summary="حذف سفارش تکی")
    def destroy(self, request, pk=None):
        try:
            self.service.delete_order(pk)
            return Response({"detail": "با موفقیت حذف شد."}, status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
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
            order = self.service.change_status(pk, data['internal_code'], request.user, data.get('description', ''))
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
