from django.urls import path, include
from .views import (
    PasswordResetConfirmAPIView,
    PasswordResetRequestAPIView,
    RefreshTokenView,
    BlackListTokenView,
    UnifiedAuthAPIView
)

app_name = "accounts"

urlpatterns = [
    # ===== Register & Login URLs ===== #
    path('auth/', UnifiedAuthAPIView.as_view(), name='auth'),
    # ===== Token URLs ===== #
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('logout/', BlackListTokenView.as_view(), name='token_blacklist'),
    # ===== Password Reset URLs ===== #
    # path('password/reset/', PasswordResetRequestAPIView.as_view(), name='password-reset-request'),
    # path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
]
