from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from ..serializers import RegisterSerializer, LoginSerializer
from apps.accounts.services import AuthService

# ======= Register API View ======= #
@extend_schema(tags=['Accounts'])
class RegisterAPIView(GenericAPIView):
    """
    ویوی ثبت نام کاربر
    با بهره گیری از ریپازیتوری و سرویس های مرتبط با کاربر، این ویو
    نقش یک انتقال دهنده و همچنین هماهنگ کننده را بازی می کندو فقط از
    متدهای مورد نظر برای ایجاد کاربر بهره می برد.
    """
    
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'accounts_register'
    
    def post(self, request, *args, **kwargs):
        """ ثبت نام کاربر با استفاده از سرویس و ریپازیتوری مورد نظر """
        # ====== اجرای سریالایزر و اعتبارسنجی ====== #
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # ====== ایجاد کاربر و ارسال ایمیل تایید ====== #
        registration_service = AuthService()
        
        # ====== ثبت نام کاربر با استفاده از سریالایزر و ریپازیتوری مورد نظر ====== #
        registered_user = registration_service.register_customer(serializer.validated_data)
        
        return Response({
                "message" : "ثبت نام با موفقیت انجام شد.",
                "username" : registered_user["user"].username,
                "token":  registered_user["tokens"]
            }, status=status.HTTP_201_CREATED)


# ====== Login API View ====== #
@extend_schema(tags=['Accounts'])
class LoginAPIView(GenericAPIView):
    """
    ورود کاربر به واسطه نام کاربری و رمز عبور
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'accounts_login'
    
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
        