from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from apps.accounts.services import TokenService
from ..serializers import RefreshTokenSerializer

# ====== Refresh Token View ====== #
@extend_schema(tags=["Accounts"])
class RefreshTokenView(GenericAPIView):
    """
    ویوی توکن دسترسی جدید برای کاربر
    فرانت اند، اطلاعات مورد نیاز که رفرش توکن کاربر هست رو از بخش توکن های
    ذخیره شده کاربر دریافت می کند. اگر که توکن دسترسی نامعتبر بود، از توکن
    رفرش استفاده می کند و به این ویو ارسال می کند. این ویوی وظیفه دارد که با
    استفاده از سرویس مورد نظر، توکن رفرش را گرفته و به واسطه آن، توکن دسترسی
    جدید را به کاربر ارسال کند و جایگزین آن کند.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RefreshTokenSerializer
    
    def post(self, request, *args, **kwargs):
        """
        ارسال توکن کاربر به سیستم و دریافت توکن جدید
        """
        # ===== دریافت توکن ===== #
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # ===== ایجاد سرویس توکن ===== #
        try:
            token_service = TokenService.refresh_token_for_user(serializer.validated_data["refresh_token"])
            return Response(token_service, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
    