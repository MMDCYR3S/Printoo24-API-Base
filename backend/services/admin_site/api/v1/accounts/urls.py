from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    StaffListCreateView, StaffDetailView, StaffBulkActionsView,
    RoleListCreateView, RoleDetailView, StaffLoginView, StaffLogoutView,
    PermissionListAPIView, CustomerBulkActionsView, CustomerListCreateView,
    CustomerDetailView, ProvinceListView, CityListView, CustomerAddressManagementView,
    CustomerAddressDetailView, RoleListView
)

urlpatterns = [
    # ===== Staff URLs ===== #
    path('staff/', StaffListCreateView.as_view(), name='staff-list-create'),
    path('staff/<int:pk>/', StaffDetailView.as_view(), name='staff-detail'),
    path('staff/actions/<str:action>/', StaffBulkActionsView.as_view(), name='staff-bulk-actions'),
    path('roles/list/', RoleListView.as_view(), name='role-list-view'),
    
    # ===== Role URLs ===== #
    # path('roles/permissions/', PermissionListAPIView.as_view(), name='permission-list'),
    # path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    # path('roles/<int:pk>/', RoleDetailView.as_view(), name='role-detail'),

    # ===== Auth URLs ===== #
    path('auth/login/', StaffLoginView.as_view(), name='staff-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='staff-token-refresh'),
    path('auth/logout/', StaffLogoutView.as_view(), name='staff-logout'),

    # ===== Customer URLs ===== #
    path('customers/', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/bulk/<str:action>/', CustomerBulkActionsView.as_view(), name='customer-bulk-actions'),
    path('customers/<int:user_id>/addresses/', CustomerAddressManagementView.as_view(), name='customer-address-list'),
    path('customers/<int:user_id>/addresses/<int:address_id>/', CustomerAddressDetailView.as_view(), name='customer-address-detail'),

    # ===== City & Province URLs ===== #
    path('geo/provinces/', ProvinceListView.as_view(), name='province-list'),
    path('geo/cities/', CityListView.as_view(), name='city-list'),
]