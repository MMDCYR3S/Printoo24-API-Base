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
# router.register(r'costs/reports', FinancialReportActionViewSet, basename='cost-report')
# router.register(r'revenues/reports', RevenueReportViewSet, basename='revenue-report')

urlpatterns = [

    # ================================= #
    # ========== CONST PATHS ========== #    
    # ================================= #
    path(
        'financial/costs/reports/', 
        FinancialReportActionViewSet.as_view({'get': 'list'}), 
        name='global-cost-reports-list'
    ),
    # ========== LIST & CREATE ========== #
    path(
        'orders/<int:order_id>/costs/reports/', 
        FinancialReportActionViewSet.as_view({'get': 'list', 'post': 'create'}), 
        name='order-cost-reports-list'
    ),
    # ========== RETRIEVE & UPDATE & DELETE ========== #
    path(
        'orders/<int:order_id>/costs/reports/<int:pk>/', 
        FinancialReportActionViewSet.as_view({
            'get': 'retrieve', 
            'patch': 'partial_update', 
            'delete': 'destroy'
        }), 
        name='order-cost-reports-detail'
    ),
    # ========== DECIDE ========== #
    path(
        'orders/<int:order_id>/costs/reports/<int:pk>/decide/', 
        FinancialReportActionViewSet.as_view({'post': 'decide'}), 
        name='order-cost-reports-decide'
    ),
    # ========== ADD ITEM ========== #
    path(
        'orders/<int:order_id>/costs/reports/<int:pk>/items/', 
        FinancialReportActionViewSet.as_view({'post': 'add_item'}), 
        name='order-cost-reports-add-item'
    ),
    # ========== DELETE ITEM & UPDATE ITEM ========== #
    path(
        'orders/<int:order_id>/costs/reports/<int:pk>/items/<int:item_id>/', 
        FinancialReportActionViewSet.as_view({
            'patch': 'update_item',
            'delete': 'delete_item'
        }), 
        name='order-cost-reports-item-detail'
    ),

    # =================================== #
    # ========== REVENUE PATHS ========== #    
    # =================================== #
    path(
        'financial/revenue/reports/', 
        RevenueReportViewSet.as_view({'get': 'list'}), 
        name='global-cost-reports-list'
    ),

    # ========== LIST & CREATE ========== #
    path(
        'orders/<int:order_id>/revenues/reports/', 
        RevenueReportViewSet.as_view({'get': 'list', 'post': 'create'}), 
        name='order-revenue-reports-list'
    ),
    
    # ========== RETRIEVE & UPDATE & DELETE ========== #
    path(
        'orders/<int:order_id>/revenues/reports/<int:pk>/', 
        RevenueReportViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy'
        }), 
        name='order-revenue-reports-detail'
    ),

    # ========== DECIDE ========== #
    path(
        'orders/<int:order_id>/revenues/reports/<int:pk>/decide/', 
        RevenueReportViewSet.as_view({'post': 'decide'}), 
        name='order-revenue-reports-decide'
    ),

    # ========== ADD ITEM ========== #
    path(
        'orders/<int:order_id>/revenues/reports/<int:pk>/items/', 
        RevenueReportViewSet.as_view({'post': 'add_item'}), 
        name='order-revenue-reports-add-item'
    ),
    # ========== DELETE ITEM & UPDATE ITEM ========== #
    path(
        'orders/<int:order_id>/revenues/reports/<int:pk>/items/<int:item_id>/', 
        RevenueReportViewSet.as_view({
            'patch': 'update_item',
            'delete': 'delete_item'
        }), 
        name='order-revenue-reports-item-detail'
    ),
    path('', include(router.urls)),
]