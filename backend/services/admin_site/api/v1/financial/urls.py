from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    FinancialInvoiceViewSet,
    FinancialTransactionViewSet,
    FinancialQuotationViewSet,
    FinancialOrderFinancialViewSet, 
    FinancialReportActionViewSet, 
    FinancialCatalogViewSet,
    BaseFinancialViewSet,
    RevenueReportViewSet
)

# ===== ایجاد روتر ===== #
router = DefaultRouter()
# router.register(r'invoices', FinancialInvoiceViewSet, basename='invoice')
# router.register(r'transactions', FinancialTransactionViewSet, basename='transaction')
# router.register(r'quotations', FinancialQuotationViewSet, basename='quotation')
# router.register(r'costs/catalogs', FinancialCatalogViewSet, basename='cost-catalog')
# router.register(r'costs/sheets', FinancialOrderFinancialViewSet, basename='order-sheet')
router.register(r'costs/reports', FinancialReportActionViewSet, basename='cost-report')
router.register(r'revenues/reports', RevenueReportViewSet, basename='revenue-report')

urlpatterns = [
    path('', include(router.urls)),
]