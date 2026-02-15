from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderListView,
    OrderDetailView,
    OrderTransitionView,
    OrderFinancialReportSubmitView,
    OrderFinancialTypeView,
    OrderFinancialCategoryView,
    OrderStatusTransactionListView,
    OrderApproveView,
    OrderRejectView,
    OrderHistoryViewSet,
    DashboardViewSet,
    # ===== فیچرهایی برای آینده ===== #
    OrderItemUploadView,
    OrderStatusGroupViewSet,
    OrderStatusViewSet,
    OrderScheduleManageView,
)

router = DefaultRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'orders/history', OrderHistoryViewSet, basename='order-history')
# router.register(r'status-groups', OrderStatusGroupViewSet, basename='status-group')
# router.register(r'statuses', OrderStatusViewSet, basename='status')

urlpatterns = [
    # ===== Order List & Detail ===== #
    path('order/list/', OrderListView.as_view(), name='admin-order-list'),
    path('order/detail/<int:pk>/', OrderDetailView.as_view(), name='admin-order-detail'),

    # ===== File Upload - Designer ===== #
    # path('items/upload/<int:item_id>/', OrderItemUploadView.as_view(), name='admin-item-upload'),

    # ===== Status Transition ===== #
    path('orders/<int:pk>/approve/', OrderApproveView.as_view(), name='order-approve'),
    path('orders/<int:pk>/reject/', OrderRejectView.as_view(), name='order-reject'),
    path('transition/<int:pk>/', OrderTransitionView.as_view(), name='admin-order-transition'),
    path('order/status/list/', OrderStatusTransactionListView.as_view(), name='order-status-list'),

    # ===== Order Financial Report Create ===== #
    path('orders/<int:pk>/costs/submit/', OrderFinancialReportSubmitView.as_view(), name='cost-report-create'),

    path('financial/tags/', OrderFinancialTypeView.as_view(), name='financial-tags'),
    path('financial/catalogs/', OrderFinancialCategoryView.as_view(), name='financial-catalogs'),
    # ===== Order Schedule ===== #
    # path('orders/<int:pk>/schedule/', OrderScheduleManageView.as_view(), name='order-schedule-manage'),
    
    # ===== Routers ===== #
    path('', include(router.urls)),
]