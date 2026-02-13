from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.operations.services.dashboard_service import DashboardAppService
from ..serializers.dashboard_serializer import (
    DesignerDashboardSerializer,
    OperationalDashboardSerializer,
    FinancialDashboardSerializer,
    AdminDashboardSerializer
)

@extend_schema(tags=['Dashboard'])
class DashboardViewSet(viewsets.ViewSet):
    """
    مجموعه APIهای داشبورد مدیریتی.
    این ویو-ست وظیفه جمع‌آوری و ارائه KPIها (شاخص‌های کلیدی عملکرد) برای نقش‌های مختلف سیستم را دارد.
    هر نقش باید فقط اندپوینت مربوط به خود را صدا بزند.
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = DashboardAppService()

    # ===== 1. DESIGNER DASHBOARD ===== #
    @extend_schema(
        summary="داشبورد اختصاصی طراح",
        description="""
        این اندپوینت شاخص‌های کلیدی برای پنل کاربری 'طراح' را برمی‌گرداند.
        
        **شاخص‌های ارائه شده:**
        1. **total_assigned:** تعداد کل سفارشاتی که در کارتابل طراحی قرار دارند (چه انجام شده چه نشده).
        2. **pending_review:** تعداد فایل‌هایی که مشتری فرستاده و طراح باید بررسی کند (مهم‌ترین عدد برای طراح).
        3. **approved:** تعداد سفارشاتی که طراح تایید کرده است.
        4. **rejected:** تعداد سفارشاتی که طراح به دلیل نقص فایل رد کرده است.
        
        **نکته فرانت:**
        از عدد `pending_review` برای نمایش Badge قرمز روی منوی سفارشات استفاده کنید.
        """,
        responses=DesignerDashboardSerializer
    )
    @action(detail=False, methods=['get'], url_path='designer')
    def designer_stats(self, request):
        stats = self.service.get_designer_stats(request.user)
        return Response(stats)

    # ===== 2. WAREHOUSE DASHBOARD ===== #
    @extend_schema(
        summary="داشبورد اختصاصی انباردار (لجستیک)",
        description="""
        این اندپوینت نمای کلی وضعیت انبار و هزینه‌های لجستیک را نمایش می‌دهد.
        
        **بخش KPI:**
        - **current_queue:** تعداد سفارشاتی که هم‌اکنون در انبار هستند (در حال پردازش یا آماده‌سازی).
        - **approved_count:** تعداد سفارشاتی که انبار تایید نهایی (خروج/ورود) کرده است.
        - **rejected_count:** تعداد مرسولات یا ورودی‌هایی که توسط انبار رد شده‌اند.
        
        **بخش نمودار (Cost Chart):**
        - لیست هزینه‌های ثبت شده توسط انبار در ۶ ماه گذشته.
        - تفکیک شده بر اساس **ماه** و **نوع هزینه** (مثلاً کارتن، پیک، پست).
        - مناسب برای رسم نمودار Stacked Bar Chart.
        """,
        responses=OperationalDashboardSerializer
    )
    @action(detail=False, methods=['get'], url_path='warehouse')
    def warehouse_stats(self, request):
        stats = self.service.get_operational_stats(
            request.user, 
            group_code='logistics',
            operation_type='logistics'
        )
        return Response(stats)

    # ===== 3. PRINT DASHBOARD ===== #
    @extend_schema(
        summary="داشبورد اختصاصی چاپخانه (تولید)",
        description="""
        این اندپوینت وضعیت صف تولید و هزینه‌های مصرفی چاپخانه را نمایش می‌دهد.
        
        **بخش KPI:**
        - **current_queue:** تعداد سفارشات در حال چاپ (زینک، برش، چاپ).
        - **approved_count:** سفارشات تکمیل شده که به مرحله بعد (انبار) ارسال شده‌اند.
        
        **بخش نمودار (Cost Chart):**
        - هزینه‌های مصرفی (کاغذ، مرکب، زینک و...) در ۶ ماه اخیر.
        - تفکیک شده بر اساس ماه.
        """,
        responses=OperationalDashboardSerializer
    )
    @action(detail=False, methods=['get'], url_path='print')
    def print_stats(self, request):
        stats = self.service.get_operational_stats(
            request.user, 
            group_code='production', 
            operation_type='print' # یا production بسته به سیدینگ
        )
        return Response(stats)

    # ===== 4. FINANCIAL DASHBOARD (EXTENDED) ===== #
    @extend_schema(
        summary="داشبورد جامع مالی (مدیر مالی)",
        description="""
        کامل‌ترین داشبورد سیستم برای رصد جریان نقدینگی و سود/زیان.
        
        **1. شاخص‌های عددی (Metrics):**
        - **All Time:** کل درآمد، هزینه و تعداد سفارشات از روز اول.
        - **This Month:** درآمد، هزینه و سود همین ماه.
        - **Avg Revenue:** میانگین مبلغ فاکتورها در این ماه.
        - **Reports:** تعداد اسناد هزینه‌ای که پرسنل ثبت کرده‌اند.
        
        **2. لیست‌ها (Top/Low Lists):**
        - **Top Selling:** ۵ سفارش با بیشترین مبلغ فروش در ماه جاری.
        - **Low Selling:** ۵ سفارش با کمترین مبلغ فروش (جهت تحلیل).
        
        **3. نمودارها (Charts Data):**
        - **daily_chart_data:** آرایه‌ای از روزهای ماه جاری. مناسب برای رسم دو نمودار خطی (Line Chart) مجزا یا ترکیبی برای "روند درآمد روزانه" و "روند هزینه روزانه".
        - **all_time_chart_data:** آرایه‌ای از ماه‌های گذشته. مناسب برای رسم نمودار میله‌ای (Bar Chart) که ستون‌های درآمد، هزینه و سود را در کنار هم برای هر ماه نشان دهد.
        """,
        responses=FinancialDashboardSerializer
    )
    @action(detail=False, methods=['get'], url_path='financial')
    def financial_stats(self, request):
        stats = self.service.get_financial_stats(request.user)
        return Response(stats)

    # ===== 5. ADMIN DASHBOARD ===== #
    @extend_schema(
        summary="داشبورد مدیریتی کل (Admin)",
        description="""
        این اندپوینت شاخص‌های کلان سیستم را برای ادمین نمایش می‌دهد.
        
        **1. بخش آمار کمی (Entity Counts):**
        - **total_staff:** تعداد کل پرسنل و کارمندان.
        - **total_customers:** تعداد کل مشتریان ثبت‌نام شده.
        - **total_orders:** تعداد کل سفارشات ثبت شده در تاریخچه سیستم.
        - **total_orders_month:** تعداد سفارشات ثبت شده در **ماه جاری**.
        
        **2. بخش وضعیت سفارشات (Status Distribution):**
        - لیستی از وضعیت‌های مختلف (مانند "در حال بررسی"، "لغو شده"، "ارسال شده") به همراه تعداد سفارشات موجود در هر وضعیت.
        - مناسب برای رسم نمودار دایره‌ای (Pie Chart) یا لیست وضعیت‌ها.
        
        **3. بخش خلاصه مالی (Financial Summary - All Time):**
        - **system_revenue:** کل درآمد سیستم از ابتدا تا کنون.
        - **system_cost:** کل هزینه‌های انجام شده از ابتدا تا کنون (شامل مواد، چاپ، لجستیک و...).
        - **system_profit:** سود خالص کل سیستم.
        """,
        responses=AdminDashboardSerializer
    )
    @action(detail=False, methods=['get'], url_path='admin')
    def admin_stats(self, request):
        stats = self.service.get_admin_stats(request.user)
        return Response(stats)