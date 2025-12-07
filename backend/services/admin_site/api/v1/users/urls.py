from django.urls import path
from .views import (
    StaffListCreateView, StaffDetailView, StaffBulkActionsView,
    RoleListCreateView, RoleDetailView
)

urlpatterns = [
    # ===== Staff URLs =====
    path('staff/', StaffListCreateView.as_view(), name='staff-list-create'),
    path('staff/<int:pk>/', StaffDetailView.as_view(), name='staff-detail'),
    path('staff/actions/<str:action>/', StaffBulkActionsView.as_view(), name='staff-bulk-actions'),
    # ===== Role URLs =====
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleDetailView.as_view(), name='role-detail'),
]