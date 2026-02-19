from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryDashboardViewSet,
    PromotionalModalViewSet,
    ContactUsViewSet,
    CustomerViewSet,
    WalletViewSet,
    SizeViewSet, 
    QuantityViewSet,
    OptionViewSet,
    ProductDashboardViewSet,
    AttachmentLibraryViewSet,
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
    ProductImageViewSet,
    InvoiceViewSet,
    QuotationViewSet,
    StaffViewSet
)

router = DefaultRouter()
router.register(r'quotations', QuotationViewSet, basename='quotation')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'categories', ProductCategoryDashboardViewSet, basename='product_category_dashboard')
router.register(r'modals', PromotionalModalViewSet, basename='promotional_modal')
router.register(r'contacts', ContactUsViewSet, basename='contact-us')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'sizes', SizeViewSet, basename='sizes')
router.register(r'quantities', QuantityViewSet, basename='quantities')
router.register(r'options', OptionViewSet, basename='options')
router.register(r'products', ProductDashboardViewSet, basename='products')
router.register(r'attachments', AttachmentLibraryViewSet, basename='attachments')
router.register(r'images', ProductImageViewSet, basename='images')
router.register(r'cart', CartDashboardViewSet, basename='cart')
router.register(r'cart-files', CartFileUploadViewSet, basename='cart-files')
router.register(r'orders', OrderDashboardViewSet, basename='orders')
router.register(r'sliders', SliderDashboardViewSet, basename='sliders')
router.register(r'provinces', ProvinceDashboardViewSet, basename='provinces')
router.register(r'cities', CityDashboardViewSet, basename='cities')
router.register(r'staffs', StaffViewSet, basename='staff')

app_name = "dashboard"

urlpatterns = [
    path("product-stats/", ProductDashboardStatsView.as_view(), name="product-stats"),
    path("user-stats/", UserDashboardStatsView.as_view(), name="user-stats"),
    path("order-stats/", OrderDashboardStatsView.as_view(), name="order-stats"),
    path('stats/financial/', FinancialDashboardStatsView.as_view(), name='dashboard-financial-stats'),
    path("", include(router.urls)),
]
