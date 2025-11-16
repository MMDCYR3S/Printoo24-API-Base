from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from ..serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from apps.accounts.services.password_reset_service import PasswordResetService
from core.common.users.user_repo import UserRepository
from core.common.users.user_services import UserService
from core.common.cache.cache_services import CacheService

# ========= Password Reset Request View ========= #
@extend_schema(tags=['Accounts'])
class PasswordResetRequestAPIView(GenericAPIView):
    """
    ویوی ای که با استفاده از ایمیل یک درخواست بازنشانی رمز عبور برای کاربر ارسال می‌کند
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    def post(self, request, *args, **kwargs):
        """
        اعتبارسنجی ایمیل و ارسال ایمیل بازنشانی رمز عبور
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # ===== ایجاد سرویس های مرتبط ===== #
        user_repo = UserRepository()
        user_service = UserService(user_repo)
        cache_service = CacheService()
        reset_service = PasswordResetService(user_service, cache_service)
        
        # ===== بازنشانی رمز عبور ===== #
        reset_service.send_reset_link(serializer.validated_data['email'])
        
        return Response(
            {"detail": "اگر ایمیل در سیستم موجود باشد، لینک بازنشانی ارسال خواهد شد."},
            status=status.HTTP_200_OK
        )

# ========= Password Reset Confirm View ========= #
@extend_schema(tags=['Accounts'])
class PasswordResetConfirmAPIView(GenericAPIView):
    """
    ویوی وارد کردن رمز عبور جدید توسط کاربر
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # ===== ایجاد سرویس های مرتبط ===== #
        user_repo = UserRepository()
        user_service = UserService(user_repo)
        cache_service = CacheService()
        reset_service = PasswordResetService(user_service, cache_service)
        
        try:
            # ===== باز کردن صفحه بازنشانی پسورد ===== #
            reset_service.confirm_password_reset(
                uidb64=uidb64,
                token=token,
                new_password=serializer.validated_data['password']
            )
        except ValidationError as e:
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"detail": "رمز عبور شما با موفقیت تغییر کرد."}, status=status.HTTP_200_OK)
