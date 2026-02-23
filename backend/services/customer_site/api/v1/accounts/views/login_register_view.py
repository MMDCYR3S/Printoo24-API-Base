from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiExample

from ..serializers import RegisterSerializer, LoginSerializer, UserDetailSerializer
from apps.accounts.services import AuthService

# ======= Register API View ======= #
@extend_schema(tags=['Accounts'])
class RegisterAPIView(GenericAPIView):
    """
    ثبت نام مستقیم کاربر.
    کاربر بلافاصله پس از ثبت نام، توکن دریافت کرده و لاگین می‌شود.
    """
    
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'accounts_register'
    serializer_class = RegisterSerializer
    
    def post(self, request, *args, **kwargs):
        """ ثبت نام کاربر با استفاده از سرویس و ریپازیتوری مورد نظر """
        # ====== اجرای سریالایزر و اعتبارسنجی ====== #
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # ====== ایجاد سرویس ====== #
        auth_service = AuthService()
        
        try:
            # ===== فراخوانی سرویس ثبت نام ===== #
            result = auth_service.register_customer(serializer.validated_data)
            
            # ===== دریافت اطلاعات کاربر ===== #
            user_instance = result["user"]
            tokens = result["tokens"]
            user_data = UserDetailSerializer(user_instance).data
            
            # ===== بازگشت اطلاعات کاربر و توکن ===== #
            return Response({
                "message": "ثبت نام با موفقیت انجام شد.",
                "user": user_data,
                "tokens": tokens
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

# ====== Login API View ====== #
@extend_schema(
    tags=['Accounts'],
    examples=[
            OpenApiExample(
                'Login Example',
                value={
                    "phone_number": "09137555555",
                    "password": "admin"
                },
                request_only=True
            ),
    ]
)
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
        phone_number = validated_data.get('phone_number')
        password = validated_data.get('password')
        
        # ===== ایجاد سرویس برای ورود ===== #
        auth_service = AuthService()
        
        try:
            # ==== اعتبارسنجی و ورود کاربر با اطلاعات داده شده ==== #
            login_data = auth_service.login_customer({"phone_number": phone_number, "password": password})
            user_instance = login_data["user"]
            tokens = login_data["tokens"]
            user_data = UserDetailSerializer(user_instance).data
            response_data = {
                "user": user_data,
                "tokens": tokens
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response({'error': e.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        