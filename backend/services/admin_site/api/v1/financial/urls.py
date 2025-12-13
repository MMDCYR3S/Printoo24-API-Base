from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FinancialCatalogViewSet, FinancialReportViewSet,
    FinancialItemViewSet, FinancialInvoiceViewSet,
    FinancialTransactionViewSet
)

router = DefaultRouter()
router.register(r'catalogs', FinancialCatalogViewSet, basename='financial-catalog')
router.register(r'reports', FinancialReportViewSet, basename='financial-report')
router.register(r'items', FinancialItemViewSet, basename='financial-item')
router.register(r'invoices', FinancialInvoiceViewSet, basename='financial-invoice')
router.register(r'transactions', FinancialTransactionViewSet, basename='financial-transaction')

urlpatterns = [
    path('', include(router.urls)),
]
