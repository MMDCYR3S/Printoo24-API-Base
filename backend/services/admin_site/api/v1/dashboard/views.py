from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiTypes, OpenApiExample, inline_serializer

from core.models import Order
from apps.dashboard.services import OrderDashboardService
from .serializers import CreateCustomOrderSerializer, OrderDashboardListSerializer, OrderDashboardDetailSerializer

# ========== VIEW SET ========== #
@extend_schema(
    tags=['Order Management'],
    summary="مدیریت سفارشات اختصاصی",
)
class OrderDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OrderDashboardService()
        
    # ========== LIST ========== #
    @extend_schema(
        summary="لیست سفارشات",
        responses=OrderDashboardListSerializer(many=True)
    )
    def list(self, request):
        queryset = Order.objects.all().order_by('-created_at')
        serializer = OrderDashboardListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # ========== RETRIEVE ========== #
    @extend_schema(
        summary="مشاهده جزئیات یک سفارش",
        description="دریافت اطلاعات کامل سفارش شامل آیتم‌ها، آدرس و وضعیت مالی.",
        responses=OrderDashboardDetailSerializer
    )
    def retrieve(self, request, id=None):
        """
        نمایش جزئیات سفارش.
        """
        try:
            order = self.service.order_repo.get_by_id(id)
            
            if not order:
                return Response({'detail': 'سفارش یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = OrderDashboardDetailSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # ========== CREATE ========== #
    @extend_schema(
        summary="ثبت سفارش اختصاصی",
        description="""
        ایجاد یک سفارش جدید توسط ادمین.
        این سفارش می‌تواند شامل محصولات سایت یا محصولات متفرقه (بدون ID محصول) باشد.
        """,
        request=CreateCustomOrderSerializer,
        responses={201: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Full Custom Order',
                summary='سفارش اختصاصی کامل',
                description='ثبت سفارش برای یک مشتری با آدرس مشخص و دو آیتم (یکی با محصول سیستم، یکی دستی).',
                value={
                    "user_id": 15,
                    "address_id": 4,
                    "description": "سفارش تلفنی - تحویل فوری",
                    "generate_invoice": True,
                    "items": [
                        {
                            "product_id": 10,
                            "quantity": 1000,
                            "price": 500,
                            "note": "کارت ویزیت سیستم"
                        },
                        {
                            "product_id": None, # محصول دستی
                            "quantity": 5,
                            "price": 250000,
                            "features": {"name": "بنر تسلیت", "size": "2x3"},
                            "note": "طراحی توسط مشتری ارسال شده"
                        }
                    ]
                },
                request_only=True
            )
        ]
    )
    def create(self, request):
        serializer = CreateCustomOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            order = self.service.create_custom_order(request.user, serializer.validated_data)
            return Response({'id': order.id, 'code': order.order_code, 'message': 'سفارش با موفقیت ثبت شد.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    # ========== 4. UPDATE ========== #
    @extend_schema(
        summary="ویرایش جزئیات سفارش",
        description="تغییر آدرس، توضیحات یا قیمت کل سفارش (فقط برای سفارشات اختصاصی).",
        request=inline_serializer(
            name='UpdateOrderPayload',
            fields={
                'address_id': serializers.IntegerField(required=False),
                'description': serializers.CharField(required=False),
                'total_price': serializers.DecimalField(max_digits=12, decimal_places=0, required=False)
            }
        ),
        examples=[
            OpenApiExample(
                'Change Address',
                value={"address_id": 8, "description": "آدرس تحویل تغییر کرد."},
                request_only=True
            )
        ]
    )
    def partial_update(self, request, id=None):
        """
        متد PATCH برای ویرایش فیلدهای خاص.
        """
        try:
            order = self.service.update_order_details(request.user, id, request.data)
            return Response({'id': order.id, 'message': 'سفارش بروزرسانی شد.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # ========== DELETE ========== #
    def destroy(self, request, id=None):
        """
        حذف سفارش
        """
        try: 
            self.service.delete_order(id)
            return Response({'success': 'سفارش با موفقیت حذف گردید.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    # ========== BULK DELETE ========== #
    @extend_schema(
        summary="حذف گروهی سفارشات",
        description="""
        حذف چندین سفارش به صورت همزمان.
        نکته: فقط سفارشاتی که فاکتور پرداخت شده ندارند و در وضعیت اولیه هستند حذف می‌شوند.
        """,
        request=inline_serializer(
            name='BulkDeletePayload',
            fields={
                'ids': serializers.ListField(child=serializers.IntegerField())
            }
        ),
        responses={200: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Delete Items',
                value={"ids": [101, 102, 105]},
                request_only=True
            )
        ]
    )
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        حذف گروهی. 
        نکته: از متد POST استفاده می‌کنیم چون ارسال Body در DELETE استاندارد نیست.
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': 'لیست شناسه (ids) الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)
            
        count = self.service.bulk_delete_orders(request.user, ids)
        return Response({'deleted_count': count, 'message': f'{count} سفارش با موفقیت حذف شدند.'})
