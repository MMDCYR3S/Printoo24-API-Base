from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes, inline_serializer
from rest_framework import serializers
from django.core.exceptions import ValidationError

from apps.dashboard.services import OrderDashboardService
from ..serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    AdminOrderCreateSerializer,
    AdminOrderUpdateSerializer,
    OrderStatusChangeSerializer,
    OrderStatusListSerializer,
    CartItemAddSimpleSerializer
)

# ===== Order Dashboard ViewSet ===== #
@extend_schema(tags=['Dashboard-Order'])
class OrderDashboardViewSet(viewsets.ViewSet):
    """
    مدیریت پیشرفته سفارشات توسط ادمین.
    شامل: لیست، جزئیات، ایجاد دستی، ویرایش کامل، تغییر وضعیت و مدیریت فایل‌ها.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OrderDashboardService()

    # ===== LIST ===== #
    @extend_schema(
        summary="لیست سفارشات",
        description="فیلتر بر اساس search (نام، موبایل، کد)، status_id و تاریخ.",
        responses=OrderListSerializer(many=True)
    )
    def list(self, request):
        queryset = self.service.get_orders_list()
        serializer = OrderListSerializer(queryset, many=True)
        return Response(serializer.data)

    # ===== RETRIEVE ===== #
    def retrieve(self, request, pk=None):
        order = self.service.get_order_detail(pk)
        if not order:
            return Response({'detail': 'سفارش یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)

    # ===== ADD ITEM TO EXISTING ORDER ===== #
    @extend_schema(
        summary="افزودن آیتم دستی به سفارش موجود",
        request=CartItemAddSimpleSerializer,
        examples=[
            OpenApiExample(
                'Manual Item Add',
                summary='افزودن آیتم دستی با قیمت دلخواه',
                value={
                    "product_slug": None,
                    "name": "هزینه بسته‌بندی ویژه صادراتی",
                    "price": 450000,
                    "selections": {"quantity": 1}
                },
                request_only=True
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
        serializer = CartItemAddSimpleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            item = self.service.add_item_to_order(pk, serializer.validated_data)
            return Response(
                {'id': item.id, 'message': 'آیتم به سفارش اضافه شد.'},
                status=status.HTTP_201_CREATED
            )
        except (ValidationError, Exception) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== CREATE ===== #
    @extend_schema(
        summary="ایجاد سفارش دستی (ادمین)",
        request=AdminOrderCreateSerializer,
        responses={201: inline_serializer(
            name='OrderCreateResp',
            fields={'id': serializers.IntegerField(), 'message': serializers.CharField()}
        )},
        examples=[
            OpenApiExample(
                '1. Existing Product with Manual Price',
                summary='محصول موجود با قیمت دستی',
                value={
                    "user_id": 10,
                    "address_id": 5,
                    "total_price": 5500000,
                    "items": [
                        {
                            "product_slug": "catalog-print",
                            "price": 5500000,
                            "selections": {"quantity": 100}
                        }
                    ]
                },
                request_only=True
            ),
            OpenApiExample(
                '2. Guest Order - Manual Service Item',
                summary='سفارش مهمان با ردیف خدماتی دستی',
                value={
                    "user_id": None,
                    "recipient_name": "شرکت نرم‌افزاری الف",
                    "recipient_phone": "09121234567",
                    "full_address": "تهران، میدان ونک، برج نگار",
                    "items": [
                        {
                            "product_slug": None,
                            "name": "هزینه فوریت در چاپ و ارسال اکسپرس",
                            "price": 850000,
                            "selections": {"quantity": 1}
                        }
                    ]
                },
                request_only=True
            )
        ]
    )
    def create(self, request):
        serializer = AdminOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        valid_data = serializer.validated_data

        try:
            order = self.service.create_admin_order(
                user_id=valid_data.get('user_id'),
                items_data=valid_data['items'],
                total_price_override=valid_data.get('total_price'),
                address_id=valid_data.get('address_id'),
                full_address=valid_data.get('full_address'),
                recipient_name=valid_data.get('recipient_name'),
                recipient_phone=valid_data.get('recipient_phone'),
                company_name=valid_data.get('company_name')
            )
            return Response(
                {'id': order.id, 'order_code': order.order_code, 'message': 'سفارش با موفقیت ثبت شد.'},
                status=status.HTTP_201_CREATED
            )
        except (ValidationError, Exception) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== UPDATE ===== #
    @extend_schema(
        summary="ویرایش اطلاعات کلی سفارش",
        request=AdminOrderUpdateSerializer,
    )
    def partial_update(self, request, pk=None):
        serializer = AdminOrderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_order = self.service.update_order_details(pk, serializer.validated_data)
            return Response(OrderDetailSerializer(updated_order).data)
        except (ValidationError, Exception) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== DESTROY ===== #
    def destroy(self, request, pk=None):
        self.service.delete_order(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== REMOVE ITEM ===== #
    @action(detail=True, methods=['delete'], url_path='items/(?P<item_id>\d+)')
    def remove_item(self, request, pk=None, item_id=None):
        """حذف تکی آیتم"""
        self.service.remove_item_from_order(pk, item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== UPLOAD FILE ===== #
    @action(
        detail=True,
        methods=['post'],
        url_path='items/(?P<item_id>\d+)/upload',
        parser_classes=[MultiPartParser, JSONParser]
    )
    def upload_file(self, request, pk=None, item_id=None):
        """آپلود فایل برای آیتم"""
        file_obj = request.FILES.get('file')

        if not file_obj:
            return Response({'detail': 'File required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = self.service.upload_order_file_async(item_id, file_obj)
            status_code = status.HTTP_202_ACCEPTED if result.get('status') == 'processing' else status.HTTP_201_CREATED
            return Response(result, status=status_code)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== GET ALL STATUSES ===== #
    @extend_schema(
        summary="دریافت لیست وضعیت‌های سفارش",
        responses=OrderStatusListSerializer(many=True)
    )
    @action(detail=False, methods=['get'], url_path='statuses')
    def get_statuses(self, request):
        statuses = self.service.get_all_order_statuses()
        serializer = OrderStatusListSerializer(statuses, many=True)
        return Response(serializer.data)

    # ===== CHANGE STATUS ===== #
    @extend_schema(
        summary="تغییر وضعیت سفارش",
        request=OrderStatusChangeSerializer,
        responses=OrderDetailSerializer
    )
    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        serializer = OrderStatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_order = self.service.change_order_status(
                order_id=pk,
                status_code=serializer.validated_data['status_code'],
                actor=request.user,
                description=serializer.validated_data.get('description')
            )
            return Response(OrderDetailSerializer(updated_order).data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== BULK DELETE ===== #
    @extend_schema(
        summary="حذف گروهی سفارشات",
        description="سفارشاتی که فاکتور نهایی یا پرداختی دارند حذف نمی‌شوند.",
        request=inline_serializer(
            name='OrderBulkDelete',
            fields={'order_ids': serializers.ListField(child=serializers.IntegerField())}
        ),
        responses={200: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Delete Draft Orders',
                value={'order_ids': [101, 102, 105]},
                request_only=True
            )
        ]
    )
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        order_ids = request.data.get('order_ids', [])

        if not order_ids:
            return Response({'detail': 'order_ids required'}, status=status.HTTP_400_BAD_REQUEST)

        result = self.service.bulk_delete_orders(order_ids)
        return Response(result)
