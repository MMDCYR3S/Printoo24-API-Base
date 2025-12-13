from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderListView,
    OrderDetailView,
    OrderItemUploadView,
    FileReviewView,
    OrderStatusGroupViewSet,
    OrderStatusViewSet,
    OrderTransitionView,
    OrderCostReportCreateView,
    CostTypeViewSet,
    OrderPrintUsageListView,
    OrderPrintUsageCreateView,
    OrderPrintUsageDetailView,
)

router = DefaultRouter()
router.register(r'status-groups', OrderStatusGroupViewSet, basename='status-group')
router.register(r'statuses', OrderStatusViewSet, basename='status')
router.register(r'cost-types', CostTypeViewSet, basename='financial-cost-type')

urlpatterns = [
    # ===== Order List & Detail ===== #
    path('order/list/', OrderListView.as_view(), name='admin-order-list'),
    path('order/detail/<int:pk>/', OrderDetailView.as_view(), name='admin-order-detail'),
    # ===== File Upload - Designer ===== #
    path('items/upload/<int:item_id>/', OrderItemUploadView.as_view(), name='admin-item-upload'),
    path('files/status/<int:file_id>/', FileReviewView.as_view(), name='admin-file-status'),
    # ===== Status Transition ===== #
    path('transition/<int:pk>/', OrderTransitionView.as_view(), name='admin-order-transition'),
    # ===== Order Cost Report Create ===== #
    path('costs/reports/<int:pk>/', OrderCostReportCreateView.as_view(), name='order-cost-report-create'),
    # ===== Order Print ===== #
    path('orders/<int:pk>/print-usages/', OrderPrintUsageCreateView.as_view(), name='print-usage-create'),
    path('orders/<int:pk>/print-usages/list/', OrderPrintUsageListView.as_view(), name='print-usage-list'),
    path('print-usages/<int:pk>/', OrderPrintUsageDetailView.as_view(), name='print-usage-detail'),
    
    # ===== Routers ===== #
    path('', include(router.urls)),
]