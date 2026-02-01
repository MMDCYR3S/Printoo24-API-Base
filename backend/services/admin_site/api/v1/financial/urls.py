from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    FinancialInvoiceViewSet,
    FinancialTransactionViewSet,
    FinancialQuotationViewSet,
    FinancialOrderCostViewSet, 
    FinancialReportActionViewSet, 
    FinancialCatalogViewSet,
    BaseFinancialViewSet
)

# ===== ایجاد روتر ===== #
router = DefaultRouter()
# router.register(r'invoices', FinancialInvoiceViewSet, basename='invoice')
# router.register(r'transactions', FinancialTransactionViewSet, basename='transaction')
# router.register(r'quotations', FinancialQuotationViewSet, basename='quotation')
# router.register(r'costs/sheets', FinancialOrderCostViewSet, basename='order-sheet')
router.register(r'costs/reports', FinancialReportActionViewSet, basename='cost-report')
# router.register(r'costs/catalogs', FinancialCatalogViewSet, basename='cost-catalog')

urlpatterns = [
    path('', include(router.urls)),
]