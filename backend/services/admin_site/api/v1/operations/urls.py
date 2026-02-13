from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderListView,
    OrderDetailView,
    OrderItemUploadView,
    OrderStatusGroupViewSet,
    OrderStatusViewSet,
    OrderTransitionView,
    OrderFinancialReportSubmitView,
    OrderScheduleManageView,
    OrderFinancialTypeView,
    OrderStatusTransactionListView,
    OrderApproveView,
    OrderRejectView
)

router = DefaultRouter()
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

    path('costs-types/', OrderFinancialTypeView.as_view(), name='order-costs'),
    # ===== Order Schedule ===== #
    # path('orders/<int:pk>/schedule/', OrderScheduleManageView.as_view(), name='order-schedule-manage'),
    
    # ===== Routers ===== #
    path('', include(router.urls)),
]