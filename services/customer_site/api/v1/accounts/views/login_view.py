from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from ..serializers import LoginSerializer
from apps.accounts.services import AuthService

# ====== Login API View ====== #
@extend_schema(tags=['Accounts'])
class LoginAPIView(GenericAPIView):
    """
    ورود کاربر به واسطه نام کاربری و رمز عبور
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        """
        ایجادن اعتبارسنجی قبل از ورود و سپس، وارد شدن
        کاربر به حساب کاربری خود
        """
        serializer = self.get_serializer(data=request.data, context={"request" : request})
        serializer.is_valid(raise_exception=True)
        
        # ===== دریافت اطلاعات از سمت کاربر ===== #
        validated_data = serializer.validated_data
        username = validated_data.get('username')
        password = validated_data.get('password')
        
        # ===== ایجاد سرویس برای ورود ===== #
        auth_service = AuthService()
        
        try:
            # ==== اعتبارسنجی و ورود کاربر با اطلاعات داده شده ==== #
            login_data = auth_service.login_customer({"username": username, "password": password})
            return Response(login_data["tokens"], status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response({'error': e.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        