from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderListView,
    OrderDetailView,
    OrderItemUploadView,
    FileStatusView,
    OrderStatusGroupViewSet,
    OrderStatusViewSet,
    OrderTransitionView,
)

router = DefaultRouter()
router.register(r'status-groups', OrderStatusGroupViewSet, basename='status-group')
router.register(r'statuses', OrderStatusViewSet, basename='status')

urlpatterns = [
    path('order/list/', OrderListView.as_view(), name='admin-order-list'),
    path('order/detail/<int:pk>/', OrderDetailView.as_view(), name='admin-order-detail'),
    # ===== File Upload - Designer ===== #
    path('items/<int:item_id>/upload/', OrderItemUploadView.as_view(), name='admin-item-upload'),
    path('files/<int:file_id>/status/', FileStatusView.as_view(), name='admin-file-status'),
    # ===== Status Transition ===== #
    path('<int:pk>/transition/', OrderTransitionView.as_view(), name='admin-order-transition'),
    # ===== Routers ===== #
    path('', include(router.urls)),
]