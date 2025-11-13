from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

from ..serializers import LoginSerializer
from apps.authentication.services import AuthService, VerificationService
from core.common.users.user_services import UserService
from core.common.users.user_repo import UserRepository

# ====== Login API View ====== #
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
        user_repo = UserRepository()
        user_service = UserService(user_repo)
        verification_service = VerificationService(user_service)
        auth_service = AuthService(user_service, verification_service)
        
        try:
            # ==== اعتبارسنجی و ورود کاربر با اطلاعات داده شده ==== #
            login_data = auth_service.login_user(username=username, password=password)
            return Response(login_data["tokens"], status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response({'error': e.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        