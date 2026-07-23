from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.dashboard.services import (
    ProductDashboardStateService, OrderDashboardStateService,
    UserDashboardStateService, FinancialDashboardStateService,
    CombinedDashboardStateService
)
from ..serializers import (
    ProductDashboardStatsSerializer, OrderDashboardStatsSerializer,
    UserDashboardStatsSerializer, FinancialDashboardStatsSerializer,
    CombinedDashboardStatsSerializer
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
        service = ProductDashboardStateService()
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
        service = OrderDashboardStateService()
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
        service = UserDashboardStateService()
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
        service = FinancialDashboardStateService()
        stats_data = service.get_financial_statistics()
        serializer = FinancialDashboardStatsSerializer(instance=stats_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ========== EXPENSE VIEW ========== #
class CombinedDashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Dashboard - States'],
        summary="دریافت تمام آمار داشبورد در یک API",
        responses={200: CombinedDashboardStatsSerializer}
    )
    def get(self, request):
        stats = CombinedDashboardStateService().get_combined_statistics()
        return Response(CombinedDashboardStatsSerializer(instance=stats).data)
