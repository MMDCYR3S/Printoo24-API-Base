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
    @extend_schema(
        summary="ایجاد سفارش دستی (توسط ادمین)",
        description="""
        این متد به ادمین اجازه می‌دهد بدون نیاز به سبد خرید، برای یک کاربر سفارش ثبت کند.
        
        **قابلیت‌ها:**
        1. **Override قیمت:** ادمین می‌تواند قیمت کل سفارش (`price`) یا قیمت هر آیتم (`item_price`) را دستی وارد کند.
        2. **محصولات متنوع:** پشتیبانی از محصولات با سایز استاندارد یا ابعاد دلخواه (متر مربعی).
        3. **انعطاف‌پذیری:** ورودی `selections` دقیقاً مشابه ساختار سبد خرید است.
        """,
        request=AdminOrderCreateSerializer, 
        responses={201: inline_serializer(name='OrderCreateSuccess', fields={'id': serializers.IntegerField(), 'message': serializers.CharField()})},
        examples=[
            OpenApiExample(
                'Scenario 1: Standard Order',
                summary='سناریو ۱: سفارش معمولی (کارت ویزیت)',
                description='ثبت سفارش برای کارت ویزیت با تیراژ ۱۰۰۰ و سایز استاندارد.',
                value={
                    "user_id": 25,
                    "address_id": 10,
                    "items": [
                        {
                            "product_slug": "business-card-glossy",
                            "selections": {
                                "quantity": 1000,
                                "size_id": 5,  # سایز استاندارد (مثلا ۹ در ۶)
                                "has_design": True,
                                "option_value_ids": [101, 205] # کاغذ گلاسه، روکش مات
                            }
                        }
                    ]
                },
                request_only=True
            ),
            OpenApiExample(
                'Scenario 2: Custom Size & Manual Price',
                summary='سناریو ۲: سفارش بنر (متراژ دلخواه) + قیمت دستی',
                description='ثبت سفارش بنر ۳ در ۱ متر. ادمین قیمت این آیتم را دستی ۵۰۰،۰۰۰ تومان تعیین می‌کند.',
                value={
                    "user_id": 25,
                    "address_id": 10,
                    "items": [
                        {
                            "product_slug": "banner-13oz",
                            "item_price": 500000,  # قیمت دستی برای این آیتم
                            "selections": {
                                "quantity": 1,
                                "custom_width": 300,  # ۳۰۰ سانتیمتر
                                "custom_height": 100, # ۱۰۰ سانتیمتر
                                "option_value_ids": [310] # پانچ: دارد
                            }
                        }
                    ],
                    "price": 550000 # قیمت کل سفارش (شامل هزینه ارسال یا خدمات اضافه)
                },
                request_only=True
            ),
            OpenApiExample(
                'Scenario 3: Multi-Item Order',
                summary='سناریو ۳: سفارش ترکیبی (چند قلم)',
                description='یک سفارش شامل تراکت و سربرگ.',
                value={
                    "user_id": 40,
                    "address_id": 12,
                    "items": [
                        {
                            "product_slug": "flyer-a5",
                            "selections": {"quantity": 2000, "size_id": 2}
                        },
                        {
                            "product_slug": "letterhead-a4",
                            "selections": {"quantity": 1000, "size_id": 1}
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
    
    # ========== BULK ACTIONS ========== #
    @extend_schema(
        summary="حذف گروهی سفارشات",
        description="""
        حذف چندین سفارش به صورت همزمان.
        **نکته مهم:** فقط سفارشاتی که در وضعیت‌های اولیه (مثل Pending یا Canceled) هستند قابل حذف می‌باشند.
        سفارشاتی که فاکتور نهایی یا پرداختی دارند حذف نمی‌شوند.
        """,
        request=inline_serializer(
            name='OrderBulkDelete',
            fields={
                'order_ids': serializers.ListField(child=serializers.IntegerField())
            }
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
        """ حذف گروهی سفارشات """
        order_ids = request.data.get('order_ids', [])

        if not order_ids:
            return Response(
                {'error': 'order_ids is required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = self.service.bulk_delete_orders(order_ids)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
