from django.urls import path, include
from .views import (
    RegisterAPIView, 
    # VerifyEmailApiView,
    LoginAPIView,
    PasswordResetConfirmAPIView,
    PasswordResetRequestAPIView,
    RefreshTokenView,
    BlackListTokenView
)

app_name = "accounts"

urlpatterns = [
    # ===== Register URLs ===== # 
    path('register/', RegisterAPIView.as_view(), name='register'),
    # path("verify/", VerifyEmailApiView.as_view(), name="verify-email"),
    # ===== Login URLs ===== #
    path('login/', LoginAPIView.as_view(), name='login'),
    # ===== Token URLs ===== #
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('logout/', BlackListTokenView.as_view(), name='token_blacklist'),
    # ===== Password Reset URLs ===== #
    path('password/reset/', PasswordResetRequestAPIView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
]
