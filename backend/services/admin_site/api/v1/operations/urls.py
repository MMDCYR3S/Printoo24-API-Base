from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderListView,
    OrderDetailView,
    OrderItemUploadView,
    OrderStatusGroupViewSet,
    OrderStatusViewSet,
    OrderTransitionView,
    OrderCostReportSubmitView,
    OrderScheduleManageView,
    OrderCostTypeView,
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
    # ===== Status Transition ===== #
    path('transition/<int:pk>/', OrderTransitionView.as_view(), name='admin-order-transition'),
    # ===== Order Cost Report Create ===== #
    path('orders/<int:pk>/costs/submit/', OrderCostReportSubmitView.as_view(), name='cost-report-create'),
    path('costs-types/', OrderCostTypeView.as_view(), name='order-costs'),
    # ===== Order Schedule ===== #
    path('orders/<int:pk>/schedule/', OrderScheduleManageView.as_view(), name='order-schedule-manage'),
    
    # ===== Routers ===== #
    path('', include(router.urls)),
]