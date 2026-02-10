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
    AdminOrderUpdateSerializer
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
    # ===== CREATE ===== #
    @extend_schema(
        summary="ایجاد سفارش دستی",
        description="ثبت سفارش برای کاربر یا مهمان. امکان تعیین سایز استاندارد (ID) یا دلخواه.",
        request=AdminOrderCreateSerializer,
        responses={201: inline_serializer(name='OrderCreateResp', fields={'id': serializers.IntegerField()})},
        examples=[
            OpenApiExample(
                '1. Standard Size (With Address ID)',
                summary='سفارش با سایز استاندارد + آدرس ذخیره شده',
                description='استفاده از size_id برای محصولاتی مثل کارت ویزیت.',
                value={
                    "user_id": 101,
                    "address_id": 5,
                    "items": [
                        {
                            "product_slug": "business-card-gl",
                            "quantity": 1000,
                            "selections": {
                                "size_id": 12,  # ID از جدول ProductSize
                                "option_value_ids": [55]
                            }
                        }
                    ]
                },
                request_only=True
            ),
            OpenApiExample(
                '2. Custom Size (Guest + Full Address)',
                summary='سفارش با سایز دلخواه + کاربر مهمان',
                description='استفاده از custom_width/height برای محصولاتی مثل بنر.',
                value={
                    "user_id": None,
                    "recipient_name": "علی رضایی",
                    "recipient_phone": "09120000000",
                    "full_address": "شیراز، خیابان زند، پلاک ۱",
                    "items": [
                        {
                            "product_slug": "banner-flex",
                            "item_price": 850000, # قیمت توافقی
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
            # ===== ایجاد از طریق سرویس ===== #
            order = self.service.create_admin_order(
                user_id=valid_data['user_id'],
                items_data=valid_data['items'],
                total_price_override=valid_data.get('price'),
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
        summary="ویرایش سفارش و آیتم‌ها",
        request=AdminOrderUpdateSerializer,
        examples=[
            OpenApiExample(
                'Update Item & Add New',
                summary='ویرایش تعداد آیتم + افزودن آیتم جدید',
                value={
                    "items": [
                        {
                            "id": 505, 
                            "quantity": 2000, # تغییر تیراژ
                            "selections": {
                                "size_id": 14 # تغییر سایز آیتم موجود!
                            }
                        },
                        {
                            "product_slug": "glue-binding", # آیتم جدید (خدمات)
                            "selections": {
                                "quantity": 2000,
                                "description": "صحافی آیتم بالا"
                            }
                        }
                    ],
                    "total_price": 5000000 # قیمت کل جدید (دستی)
                },
                request_only=True
            )
        ]
    )
    def partial_update(self, request, pk=None):
        serializer = AdminOrderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            updated_order = self.service.update_full_order(pk, serializer.validated_data)
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

    # ===== اصلاحیه: اکشن درست ===== #
    @action(detail=True, methods=['post'], url_path='items/(?P<item_id>\d+)/upload', parser_classes=[MultiPartParser])
    def upload_file(self, request, pk=None, item_id=None):
        """ آپلود فایل برای آیتم """
        # ===== دریافت فایل ها از 
        file_obj = request.FILES.get('file')
        # ===== بررسی وجود فایل ===== #
        if not file_obj:
             return Response({'detail': 'File required'}, status=status.HTTP_400_BAD_REQUEST)
        # ===== آپلود ===== #
        try:
            result = self.service.upload_order_file_async(item_id, file_obj)
            status_code = status.HTTP_202_ACCEPTED if result.get('status') == 'processing' else status.HTTP_201_CREATED
            return Response(result, status=status_code)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # ========== BULK ACTIONS ========== #
    # @extend_schema(
    #     summary="حذف گروهی سفارشات",
    #     description="""
    #     حذف چندین سفارش به صورت همزمان.
    #     **نکته مهم:** فقط سفارشاتی که در وضعیت‌های اولیه (مثل Pending یا Canceled) هستند قابل حذف می‌باشند.
    #     سفارشاتی که فاکتور نهایی یا پرداختی دارند حذف نمی‌شوند.
    #     """,
    #     request=inline_serializer(
    #         name='OrderBulkDelete',
    #         fields={
    #             'order_ids': serializers.ListField(child=serializers.IntegerField())
    #         }
    #     ),
    #     responses={200: OpenApiTypes.OBJECT},
    #     examples=[
    #         OpenApiExample(
    #             'Delete Draft Orders',
    #             value={'order_ids': [101, 102, 105]},
    #             request_only=True
    #         )
    #     ]
    # )
    # ===== BULK DELETE ===== #
    @extend_schema(request=inline_serializer(name='BulkDel', fields={'ids': serializers.ListField()}))
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
             return Response({'detail': 'ids required'}, status=status.HTTP_400_BAD_REQUEST)
        
        result = self.service.bulk_delete_orders(ids)
        return Response(result)
