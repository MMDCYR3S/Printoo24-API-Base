from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderListView,
    OrderDetailView,
    OrderItemUploadView,
    OrderStatusGroupViewSet,
    OrderStatusViewSet,
    OrderTransitionView,
    
    OrderPrintUsageListView,
    OrderPrintUsageCreateView,
    OrderPrintUsageDetailView,
    OrderItemStatusUpdateView,
    OrderCostReportSubmitView,
)

router = DefaultRouter()
router.register(r'status-groups', OrderStatusGroupViewSet, basename='status-group')
router.register(r'statuses', OrderStatusViewSet, basename='status')

urlpatterns = [
    # ===== Order List & Detail ===== #
    path('order/list/', OrderListView.as_view(), name='admin-order-list'),
    path('order/detail/<int:pk>/', OrderDetailView.as_view(), name='admin-order-detail'),
    # ===== File Upload - Designer ===== #
    path('items/upload/<int:item_id>/', OrderItemUploadView.as_view(), name='admin-item-upload'),
    path('order/item/<int:pk>/status/', OrderItemStatusUpdateView.as_view(), name='order-item-status-update'),
    # ===== Status Transition ===== #
    path('transition/<int:pk>/', OrderTransitionView.as_view(), name='admin-order-transition'),
    # ===== Order Cost Report Create ===== #
    path('orders/<int:pk>/costs/submit/', OrderCostReportSubmitView.as_view(), name='cost-report-create'),
    # ===== Order Print ===== #
    path('orders/<int:pk>/print-usages/', OrderPrintUsageCreateView.as_view(), name='print-usage-create'),
    path('orders/<int:pk>/print-usages/list/', OrderPrintUsageListView.as_view(), name='print-usage-list'),
    path('print-usages/<int:pk>/', OrderPrintUsageDetailView.as_view(), name='print-usage-detail'),
    
    # ===== Routers ===== #
    path('', include(router.urls)),
]