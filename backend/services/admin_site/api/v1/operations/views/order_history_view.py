from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema

from apps.operations.services.order_history_service import OrderHistoryAppService
from ..serializers import OrderHistoryResponseSerializer, GlobalOrderLogSerializer

# ===== PAGINATION CLASS ===== #
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# ===== ORDER HISTORY VIEWSET ===== #
@extend_schema(tags=['Operations - Order History'])
class OrderHistoryViewSet(viewsets.ViewSet):
    """
    مشاهده تایم‌لاین و تاریخچه تغییرات وضعیت سفارش.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OrderHistoryAppService()

    @extend_schema(
        summary="دریافت تاریخچه تغییرات وضعیت یک سفارش",
        description="""
        این متد لیست کامل تغییرات وضعیت (از چه وضعیتی -> به چه وضعیتی) را به همراه
        نام کاربر تغییر دهنده و دلیل (Description) برمی‌گرداند.
        مناسب برای ردیابی علت رد شدن سفارشات.
        """,
        responses={200: OrderHistoryResponseSerializer}
    )
    def retrieve(self, request, pk=None):
        """
        pk: Order ID
        """
        data = self.service.get_order_history_details(request.user, order_id=pk)
        serializer = OrderHistoryResponseSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="لیست جامع تغییرات وضعیت سیستم",
        description="""
        نمایش تمام تغییر وضعیت‌های انجام شده در سیستم به ترتیب جدیدترین.
        شامل نام تغییر دهنده، نام سفارش و وضعیت‌های مبدا و مقصد.
        """,
        responses={200: GlobalOrderLogSerializer(many=True)}
    )
    def list(self, request):
        """
        نمایش لیست کلی لاگ‌ها (Timeline)
        """
        # ===== دریافت لاگ‌ها ===== #
        queryset = self.service.get_all_logs(request.user)

        # ===== اعمال Pagination ===== #
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)

        if page is not None:
            serializer = GlobalOrderLogSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # حالت Fallback اگر Pagination کار نکرد
        serializer = GlobalOrderLogSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

