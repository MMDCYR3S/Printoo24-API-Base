from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.dashboard.services import (
    ProductDashboardService, OrderDashboardService,
    UserDashboardService, FinancialDashboardService
)
from ..serializers import (
    ProductDashboardStatsSerializer, OrderDashboardStatsSerializer,
    UserDashboardStatsSerializer, FinancialDashboardStatsSerializer
)

# ========== PRODUCT VIEW ========== #
class ProductDashboardStatsView(APIView):
    """
    API برای دریافت آمار خلاصه محصولات در داشبورد ادمین.
    """
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        tags=['Dashboard - States'],
        summary="دریافت آمار کلی محصولات",
        responses={200: ProductDashboardStatsSerializer}
    )
    def get(self, request):
        # ===== دریافت آمار کلی محصولات ===== #
        service = ProductDashboardService()
        stats_data = service.get_product_statistics()
        
        # ===== دریافت سریالایزر ===== #
        serializer = ProductDashboardStatsSerializer(instance=stats_data)
        
        # ===== دریافت پاسخ نهایی ===== #
        return Response(serializer.data, status=status.HTTP_200_OK)

# ========== ORDER VIEW ========== #
class OrderDashboardStatsView(APIView):
    """
    API برای دریافت آمار خلاصه سفارشات در داشبورد ادمین.
    شامل تعداد کل، درصد رشد، و سفارشات در انتظار تایید (PENDING_INITIAL_ADMIN).
    """
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        tags=['Dashboard - States'],
        summary="دریافت آمار کلی سفارشات",
        responses={200: OrderDashboardStatsSerializer}
    )
    def get(self, request):
        service = OrderDashboardService()
        stats_data = service.get_order_statistics()
        serializer = OrderDashboardStatsSerializer(instance=stats_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ========== USER VIEW ========== #
class UserDashboardStatsView(APIView):
    """
    API برای دریافت آمار خلاصه کاربران در داشبورد ادمین.
    شامل تعداد کل، رشد ماهانه، وضعیت فعال/غیرفعال و تفکیک نقش‌ها.
    """
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        tags=['Dashboard - States'],
        summary="دریافت آمار کلی کاربران",
        responses={200: UserDashboardStatsSerializer}
    )
    def get(self, request):
        service = UserDashboardService()
        stats_data = service.get_user_statistics()
        serializer = UserDashboardStatsSerializer(instance=stats_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ========== FINANCIAL VIEW ========== #
class FinancialDashboardStatsView(APIView):
    """
    API داشبورد مالی.
    شامل درآمد کل، رشد ماهانه و داده‌های نمودار فروش ۳۰ روزه.
    """
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        tags=['Dashboard - States'],
        summary="دریافت آمار مالی و نمودار فروش",
        responses={200: FinancialDashboardStatsSerializer}
    )
    def get(self, request):
        service = FinancialDashboardService()
        stats_data = service.get_financial_statistics()
        serializer = FinancialDashboardStatsSerializer(instance=stats_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
