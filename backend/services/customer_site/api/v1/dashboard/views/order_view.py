from jsonschema import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes, inline_serializer
from rest_framework import serializers

from apps.dashboard.services import OrderDashboardService
from ..serializers import (
    OrderListSerializer, 
    OrderDetailSerializer, 
    AdminOrderCreateSerializer,
    AdminOrderUpdateSerializer,
    OrderStatusChangeSerializer,
    OrderStatusListSerializer
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
        description="قابلیت فیلتر بر اساس search (نام، موبایل، کد)، status_id و تاریخ.",
        responses=OrderListSerializer(many=True)
    )
    def list(self, request):
        filters = {
            'search': request.query_params.get('search'),
            'status_id': request.query_params.get('status_id'),
            'date_from': request.query_params.get('date_from'),
            'date_to': request.query_params.get('date_to'),
        }
        queryset = self.service.get_orders_list()
        
        serializer = OrderListSerializer(queryset, many=True)
        return Response(serializer.data)

    # ===== RETRIEVE ===== #
    @extend_schema(responses=OrderDetailSerializer)
    def retrieve(self, request, pk=None):
        try:
            order = self.service.get_order_detail(pk)
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data)
        except Exception:
            return Response({'detail': 'سفارش یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

    # ===== CREATE ===== #
    @extend_schema(
        summary="ایجاد سفارش دستی",
        description="ثبت سفارش برای کاربر یا مهمان. امکان تعیین قیمت کل به صورت دستی (total_price) و اطلاعات کامل مشتری.",
        request=AdminOrderCreateSerializer,
        responses={201: inline_serializer(name='OrderCreateResp', fields={'id': serializers.IntegerField(), 'message': serializers.CharField()})},
        examples=[
            OpenApiExample(
                '1. Standard Size (With Price Override)',
                summary='سفارش با سایز استاندارد + قیمت کل دستی',
                description='تعیین دستی مبلغ کل سفارش با نادیده گرفتن قیمت پایه محصول.',
                value={
                    "user_id": 101,
                    "address_id": 5,
                    "total_price": 5000000, # <--- قیمت کل دستی
                    "items": [
                        {
                            "product_slug": "business-card-gl",
                            "quantity": 1000,
                            "selections": {
                                "size_id": 12,
                                "option_value_ids": [55]
                            }
                        }
                    ]
                },
                request_only=True
            ),
            OpenApiExample(
                '2. Custom Size (Guest User)',
                summary='سفارش با سایز دلخواه + کاربر مهمان',
                description='ثبت اطلاعات کامل آدرس و گیرنده به صورت متنی.',
                value={
                    "user_id": None,
                    "recipient_name": "علی رضایی",
                    "recipient_phone": "09120000000",
                    "full_address": "شیراز، خیابان زند، پلاک ۱",
                    "total_price": 850000,
                    "items": [
                        {
                            "product_slug": "banner-flex",
                            "selections": {
                                "quantity": 1,
                                "custom_width": 350.5,
                                "custom_height": 120,
                                "name": "بنر سردر مغازه"
                            }
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
                user_id=valid_data['user_id'],
                items_data=valid_data['items'],
                total_price_override=valid_data.get('total_price'), # <--- باگ اصلاح شد (به جای price)
                address_id=valid_data.get('address_id'),
                full_address=valid_data.get('full_address'),
                recipient_name=valid_data.get('recipient_name'),
                recipient_phone=valid_data.get('recipient_phone'),
                company_name=valid_data.get('company_name')
            )
            return Response({'id': order.id, 'message': 'سفارش ثبت شد.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== UPDATE ===== #
    @extend_schema(
        summary="ویرایش اطلاعات کلی سفارش",
        description="تغییر آدرس، نوع سفارش و مهم‌تر از همه: مبلغ کل سفارش (total_price).",
        request=AdminOrderUpdateSerializer,
        examples=[
            OpenApiExample(
                'Update Base Data',
                summary='تغییر قیمت کل و نوع سفارش',
                value={
                    "type": "2",
                    "total_price": 6500000 # قیمت آپدیت شده دستی
                },
                request_only=True
            )
        ]
    )
    def partial_update(self, request, pk=None):
        serializer = AdminOrderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # <--- باگ متد ناموجود در سرویس اصلاح شد --->
            updated_order = self.service.update_order_details(pk, serializer.validated_data)
            return Response(OrderDetailSerializer(updated_order).data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== DESTROY ===== #
    def destroy(self, request, pk=None):
        self.service.delete_order(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== REMOVE ITEM ===== #
    @action(detail=True, methods=['delete'], url_path='items/(?P<item_id>\d+)')
    def remove_item(self, request, pk=None, item_id=None):
        """ حذف تکی آیتم """
        self.service.remove_item_from_order(pk, item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== UPLOAD FILE ===== #
    @action(detail=True, methods=['post'], url_path='items/(?P<item_id>\d+)/upload', parser_classes=[MultiPartParser, JSONParser])
    def upload_file(self, request, pk=None, item_id=None):
        """ آپلود فایل برای آیتم """
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
        
        status_code = serializer.validated_data['status_code']
        description = serializer.validated_data.get('description')

        try:
            updated_order = self.service.change_order_status(
                order_id=pk,
                status_code=status_code,
                description=description
            )
            return Response(OrderDetailSerializer(updated_order).data, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
             return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # ========== BULK ACTIONS ========== #
    @extend_schema(
        summary="حذف گروهی سفارشات",
        description="حذف چندین سفارش. سفارشاتی که فاکتور نهایی یا پرداختی دارند حذف نمی‌شوند.",
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
