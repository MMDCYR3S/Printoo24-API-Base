from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryDashboardViewSet,
    PromotionalModalViewSet,
    ContactUsViewSet,
    CustomerViewSet,
    WalletViewSet,
    SizeViewSet, 
    MaterialViewSet,
    QuantityViewSet,
    FileUploadSpecViewSet,
    OptionViewSet,
    ProductDashboardViewSet,
    AttachmentLibraryViewSet,
    CartDashboardViewSet,
    CartFileUploadViewSet,
    OrderDashboardViewSet,
)

router = DefaultRouter()
router.register(r'categories', ProductCategoryDashboardViewSet, basename='product_category_dashboard')
router.register(r'modals', PromotionalModalViewSet, basename='promotional_modal')
router.register(r'contacts', ContactUsViewSet, basename='contact_us')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'sizes', SizeViewSet, basename='sizes')
router.register(r'materials', MaterialViewSet, basename='materials')
router.register(r'quantities', QuantityViewSet, basename='quantities')
router.register(r'file-specs', FileUploadSpecViewSet, basename='file-specs')
router.register(r'options', OptionViewSet, basename='options')
router.register(r'products', ProductDashboardViewSet, basename='products')
router.register(r'attachments', AttachmentLibraryViewSet, basename='attachments')
router.register(r'cart', CartDashboardViewSet, basename='cart')
router.register(r'cart-files', CartFileUploadViewSet, basename='cart-files')
router.register(r'orders', OrderDashboardViewSet, basename='orders')

app_name = "dashboard"

urlpatterns = [
    path("", include(router.urls)),
]
