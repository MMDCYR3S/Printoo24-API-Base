from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryDashboardViewSet,
    PromotionalModalViewSet,
    ContactUsViewSet,
    CustomerViewSet,
    WalletViewSet,
    ProductDashboardViewSet,
    CartDashboardViewSet,
    CartFileUploadViewSet,
    OrderDashboardViewSet,
    SliderDashboardViewSet,
    ProductDashboardStatsView,
    UserDashboardStatsView,
    OrderDashboardStatsView,
    FinancialDashboardStatsView,
    CityDashboardViewSet,
    ProvinceDashboardViewSet,
    InvoiceViewSet,
    QuotationViewSet,
    StaffViewSet,
    SiteMediaDashboardViewSet,
    TutorialViewSet,
    ArticleViewSet,
    ArticleCategoryViewSet,
    ProductSelectorViewSet,
    ExpenseViewSet,
    CombinedDashboardStatsView,
)

router = DefaultRouter()
router.register(r'quotations', QuotationViewSet, basename='quotation')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'categories', ProductCategoryDashboardViewSet, basename='product_category_dashboard')
router.register(r'modals', PromotionalModalViewSet, basename='promotional_modal')
router.register(r'contacts', ContactUsViewSet, basename='contact-us')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'products', ProductDashboardViewSet, basename='products')
router.register(r'cart', CartDashboardViewSet, basename='cart')
router.register(r'cart-files', CartFileUploadViewSet, basename='cart-files')
router.register(r'orders', OrderDashboardViewSet, basename='orders')
router.register(r'sliders', SliderDashboardViewSet, basename='sliders')
router.register(r'site-media', SiteMediaDashboardViewSet, basename='site-media')
router.register(r'provinces', ProvinceDashboardViewSet, basename='provinces')
router.register(r'cities', CityDashboardViewSet, basename='cities')
router.register(r'staffs', StaffViewSet, basename='staff')
router.register(r'blog-categories', ArticleCategoryViewSet, basename='dashboard-blog-category')
router.register(r'articles', ArticleViewSet, basename='dashboard-article')
router.register(r'tutorials', TutorialViewSet, basename='dashboard-tutorial')
router.register(r'products-minimal', ProductSelectorViewSet, basename='dashboard-product-minimal')
router.register(r'expenses', ExpenseViewSet, basename='expense')

app_name = "dashboard"

urlpatterns = [
    path("product-stats/", ProductDashboardStatsView.as_view(), name="product-stats"),
    path("user-stats/", UserDashboardStatsView.as_view(), name="user-stats"),
    path("order-stats/", OrderDashboardStatsView.as_view(), name="order-stats"),
    path('stats/financial/', FinancialDashboardStatsView.as_view(), name='dashboard-financial-stats'),
    path('stats/', CombinedDashboardStatsView.as_view(), name='dashboard-combined-stats'),
    path("", include(router.urls)),
]
