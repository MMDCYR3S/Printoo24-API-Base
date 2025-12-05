from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema

from apps.dashboard.services import OrderDashboardService
from ..serializers import (
    OrderListSerializer, 
    OrderDetailSerializer, 
    AdminOrderCreateSerializer,
    AdminOrderUpdateSerializer
)

# ===== Order Dashboard ViewSet ===== #
@extend_schema(tags=['Dashboard-Order'])
class OrderDashboardViewSet(viewsets.ViewSet):
    """
    مدیریت سفارشات (Order Management) برای ادمین.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OrderDashboardService()

    # ===== لیست سفارشات ===== #
    @extend_schema(responses=OrderListSerializer(many=True))
    def list(self, request):
        queryset = self.service.get_all_orders_queryset()
        # اینجا باید Paginate کنید
        serializer = OrderListSerializer(queryset, many=True)
        return Response(serializer.data)

    # ===== جزئیات سفارش ===== #
    @extend_schema(responses=OrderDetailSerializer)
    def retrieve(self, request, pk=None):
        order = self.service.get_order_detail(pk)
        if not order:
            return Response({'detail': 'سفارش یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)

    # ===== ایجاد سفارش دستی ===== #
    @extend_schema(request=AdminOrderCreateSerializer, responses=OrderDetailSerializer)
    def create(self, request):
        serializer = AdminOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            order = self.service.create_admin_order(
                user_id=serializer.validated_data['user_id'],
                address_id=serializer.validated_data['address_id'],
                items_data=serializer.validated_data['items'],
                total_price_override=serializer.validated_data.get('price')
            )
            return Response({'id': order.id, 'message': 'سفارش با موفقیت ثبت شد.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== ویرایش سفارش (Partial) ===== #
    @extend_schema(request=AdminOrderUpdateSerializer)
    def partial_update(self, request, pk=None):
        """ تغییر آدرس یا نوع سفارش (بدون تغییر وضعیت) """
        serializer = AdminOrderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.service.update_order_details(pk, serializer.validated_data)
        return Response({'status': 'Order updated'})

    # ===== حذف سفارش ===== #
    def destroy(self, request, pk=None):
        self.service.delete_order(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== حذف آیتم از سفارش ===== #
    @action(detail=True, methods=['delete'], url_path='items/(?P<item_id>\d+)')
    def remove_item(self, request, pk=None, item_id=None):
        self.service.remove_item_from_order(pk, item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== اصلاحیه: اکشن درست ===== #
    @action(detail=True, methods=['post'], url_path='items/(?P<item_id>\d+)/upload', parser_classes=[MultiPartParser, JSONParser])
    def upload_file_for_item(self, request, pk=None, item_id=None):
        """
        آپلود فایل برای یک آیتم خاص از سفارش.
        pk: Order ID
        item_id: OrderItem ID
        """
        file_obj = request.FILES.get('file')
        req_id = request.data.get('requirement_id')
        
        if not file_obj or not req_id:
             return Response({'detail': 'File and requirement_id required'}, status=status.HTTP_400_BAD_REQUEST)

        # ===== بررسی وجود فایل از قبل و جایگزینی ===== #
        
        # ===== فراخوانی سرویس ===== #
        result = self.service.upload_order_file_async(
            order_item_id=item_id,
            requirement_id=req_id,
            file_obj=file_obj
        )
        
        if result['status'] == 'processing':
            return Response(result, status=status.HTTP_202_ACCEPTED)
        
        return Response(result, status=status.HTTP_201_CREATED)