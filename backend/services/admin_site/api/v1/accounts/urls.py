from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    StaffListCreateView, StaffDetailView, StaffBulkActionsView,
    RoleListCreateView, RoleDetailView, StaffLoginView, StaffLogoutView
)

urlpatterns = [
    # ===== Staff URLs ===== #
    path('staff/', StaffListCreateView.as_view(), name='staff-list-create'),
    path('staff/<int:pk>/', StaffDetailView.as_view(), name='staff-detail'),
    path('staff/actions/<str:action>/', StaffBulkActionsView.as_view(), name='staff-bulk-actions'),
    # ===== Role URLs ===== #
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleDetailView.as_view(), name='role-detail'),
    # ===== Auth URLs ===== #
    path('auth/login/', StaffLoginView.as_view(), name='staff-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='staff-token-refresh'),
    path('auth/logout/', StaffLogoutView.as_view(), name='staff-logout'),
]