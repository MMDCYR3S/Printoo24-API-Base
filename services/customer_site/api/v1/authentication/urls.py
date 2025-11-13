from django.urls import path, include
from .views import (
    RegisterAPIView, 
    VerifyEmailApiView,
    LoginAPIView,
    LogoutAPIView,
    PasswordResetConfirmAPIView,
    PasswordResetRequestAPIView
)
urlpatterns = [
    # ===== Register URLs ===== # 
    path('register/', RegisterAPIView.as_view(), name='register'),
    path("verify/", VerifyEmailApiView.as_view(), name="verify-email"),
    # ===== Login URLs ===== #
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    # ===== Password Reset URLs ===== #
    path('password/reset/', PasswordResetRequestAPIView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
]
