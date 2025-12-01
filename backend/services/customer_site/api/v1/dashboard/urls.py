from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryDashboardViewSet,
    PromotionalModalViewSet,
    ContactUsViewSet,
    CustomerViewSet,
    WalletViewSet
)

router = DefaultRouter()
router.register('categories', ProductCategoryDashboardViewSet, basename='product_category_dashboard')
router.register('modals', PromotionalModalViewSet, basename='promotional_modal')
router.register('contacts', ContactUsViewSet, basename='contact_us')
router.register('customers', CustomerViewSet, basename='customer')
router.register('wallets', WalletViewSet, basename='wallet')

app_name = "dashboard"

urlpatterns = [
    path("", include(router.urls)),
]
