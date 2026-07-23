from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status

# ====== Custom Refresh View ====== #
@extend_schema(
    tags=['Accounts'],
    summary="دریافت اکسس توکن جدید (Refresh)",
    description="با ارسال رفرش توکن معتبر، یک اکسس توکن جدید دریافت کنید.",
    responses={
        status.HTTP_200_OK: OpenApiResponse(description="توکن جدید صادر شد"),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="رفرش توکن نامعتبر یا منقضی شده است"),
    }
)
class RefreshTokenView(TokenRefreshView):
    pass

# ====== Custom Blacklist (Logout) View ====== #
@extend_schema(
    tags=['Accounts'],
    summary="خروج از حساب (Blacklist Token)",
    description="رفرش توکن را به لیست سیاه اضافه می‌کند تا دیگر قابل استفاده نباشد (Logout).",
    responses={
        status.HTTP_200_OK: OpenApiResponse(description="خروج با موفقیت انجام شد"),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="توکن نامعتبر است"),
    }
)
class BlackListTokenView(TokenBlacklistView):
    pass