from django.urls import path
from .views import OrderListView, OrderDetailView

urlpatterns = [
    path('order/list/', OrderListView.as_view(), name='admin-order-list'),
    path('order/detail/<int:pk>/', OrderDetailView.as_view(), name='admin-order-detail'),
]