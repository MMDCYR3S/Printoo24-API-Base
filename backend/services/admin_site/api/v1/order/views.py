from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiTypes, OpenApiExample, inline_serializer

from core.models import Order
from apps.order.services import OrderDashboardService
from .serializers import (
    CreateCustomOrderSerializer, 
    OrderDashboardListSerializer, 
    OrderDashboardDetailSerializer,
    OrderDashboardUpdateSerializer
)

# ========== ORDER VIEW SET ========== #
@extend_schema(tags=['Admin - Order Management'])
class OrderDashboardViewSet(viewsets.ViewSet):
    """
    مدیریت سفارشات اختصاصی و سیستمی (پنل ادمین).
    """
    permission_classes = [IsAdminUser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OrderDashboardService()

    # ========== LIST ========== #
    @extend_schema(
        summary="لیست سفارشات",
        responses=OrderDashboardListSerializer(many=True)
    )
    def list(self, request):
        queryset = self.service.get_all_orders_queryset()
        # در پروژه واقعی: اضافه کردن Pagination
        serializer = OrderDashboardListSerializer(queryset, many=True)
        return Response(serializer.data)

    # ========== RETRIEVE ========== #
    @extend_schema(
        summary="مشاهده جزئیات سفارش",
        responses=OrderDashboardDetailSerializer
    )
    def retrieve(self, request, pk=None):
        order = self.service.get_order_detail(pk)
        if not order:
            return Response({'detail': 'سفارش یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderDashboardDetailSerializer(order)
        return Response(serializer.data)

    # ========== CREATE ========== #
    @extend_schema(
        summary="ثبت سفارش اختصاصی",
        description="ایجاد سفارش جدید توسط ادمین با قابلیت تعیین قیمت و جزئیات دستی.",
        request=CreateCustomOrderSerializer,
        examples=[
            OpenApiExample(
                'Custom Order Example',
                value={
                    "user_id": 10,
                    "address_id": 5,
                    "description": "سفارش تلفنی",
                    "price": 5000000, # قیمت کل دستی
                    "items": [
                        {
                            "product_slug": "banner-13oz",
                            "quantity": 1,
                            "selections": {
                                "custom_width": 300,
                                "custom_height": 100,
                                "option_value_ids": [10, 12]
                            }
                        }
                    ]
                }
            ),
            OpenApiExample(
                'Single Response',
                summary='سفارش اختصاصی(بدون محصول)',
                value={
                    "recipient_name": "محمد باقری",
                    "recipient_phone": "09137514625",
                    "company_name": "شرکت صحابی",
                    "full_address": "اصفهان - خیابان آزادی - جنب مترو",
                    "price": 2210000,
                    "items": [
                        {
                            "name": "طراحی لوگو اختصاصی",
                            "description": "سفارش اختصاصی",
                            "item_price": 500000,
                            "quantity": 12,
                            "description": "طبق گفتگوی تلفنی",
                            "selections": {
                                "paper_type": "گلاسه ۳۰۰ گرم",
                                "coating": "UV",
                                "special_request": {
                                    "value" : "دور بر سیمی",
                                    "price": 20000
                                },
                                "color": [
                                    "آبی",
                                    "قرمز",
                                    "مشکی"
                                ]
                            }
                        }
                    ]
                }
            )
        ]
    )
    def create(self, request):
        serializer = CreateCustomOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            # فراخوانی سرویس اپلیکیشن
            order = self.service.create_custom_order(
                admin_user=request.user,
                data=data # دیکشنری کامل (user_id, address_id, items, price)
            )
            return Response(
                {'id': order.id, 'code': order.order_code, 'message': 'سفارش با موفقیت ثبت شد.'}, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== PARTIAL UPDATE ========== #
    @extend_schema(summary="ویرایش جزئیات سفارش", request=OrderDashboardUpdateSerializer)
    def partial_update(self, request, pk=None):
        serializer = OrderDashboardUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            self.service.update_order_details(request.user, pk, data=data)
            return Response({'status': 'Order updated'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== DELETE ========== #
    def destroy(self, request, pk=None):
        self.service.delete_order(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ========== BULK DELETE ========== #
    @extend_schema(
        summary="حذف گروهی سفارشات",
        request=inline_serializer(name='BulkDelete', fields={'ids': serializers.ListField()})
    )
    @action(detail=False, methods=['delete', 'post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': 'ids required'}, status=400)
            
        result = self.service.bulk_delete_orders(request.user, ids)
        return Response(result)