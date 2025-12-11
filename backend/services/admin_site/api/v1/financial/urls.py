from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinancialCatalogViewSet, FinancialReportViewSet, FinancialItemViewSet

router = DefaultRouter()
router.register(r'catalogs', FinancialCatalogViewSet, basename='financial-catalog')
router.register(r'reports', FinancialReportViewSet, basename='financial-report')
router.register(r'items', FinancialItemViewSet, basename='financial-item')

urlpatterns = [
    path('', include(router.urls)),
]
