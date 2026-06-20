from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiExample

from ..serializers import UnifiedAuthSerializer, UserDetailSerializer
from apps.accounts.services import AuthService

@extend_schema(
    tags=['Accounts'],
    examples=[
        OpenApiExample(
            'Login/Register Example',
            value={
                'phone_number': '09137555555',
                'password': 'admin'
            },
            request_only=True,
            description='شماره تماس و رمز عبور برای ورود یا ثبت‌نام'
        ),
        OpenApiExample(
            'Login Success Response',
            value={
                'message': 'چوونەژوورەوە بە سەرکەوتوویی ئەنجامدرا.',
                'user': {
                    'id': 1,
                    'phone_number': '09137555555',
                    'first_name': '',
                    'last_name': ''
                },
                'tokens': {
                    'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                    'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                }
            },
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Register Success Response',
            value={
                'message': 'خۆتۆمارکردن و چوونەژوورەوە بە سەرکەوتوویی ئەنجامدرا.',
                'user': {
                    'id': 2,
                    'phone_number': '09137555555',
                    'first_name': '',
                    'last_name': ''
                },
                'tokens': {
                    'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                    'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                }
            },
            response_only=True,
            status_codes=['201']
        )
    ]
)
class UnifiedAuthAPIView(GenericAPIView):
    """
    API یکپارچه ورود و ثبت‌نام.
    با دریافت شماره تماس و رمز عبور:
    ۱. اگر شماره تماس موجود بود -> کاربر لاگین می‌شود.
    ۲. اگر موجود نبود -> ثبت‌نام انجام شده و سپس لاگین می‌شود.
    """
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    serializer_class = UnifiedAuthSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        auth_service = AuthService()
        
        try:
            # ===== فراخوانی سرویس احراز هویت ===== #
            result = auth_service.authenticate_or_register(serializer.validated_data)
            
            user_instance = result["user"]
            tokens = result["tokens"]
            action = result.get("action")
            
            user_data = UserDetailSerializer(user_instance).data
            
            # ===== تنظیم پیام ===== # 
            message = "چوونەژوورەوە بە سەرکەوتوویی ئەنجامدرا." if action == 'login' else "خۆتۆمارکردن و چوونەژوورەوە بە سەرکەوتوویی ئەنجامدرا."
            status_code = status.HTTP_200_OK if action == 'login' else status.HTTP_201_CREATED
            
            return Response({
                "message": message,
                "user": user_data,
                "tokens": tokens
            }, status=status_code)
            
        except ValidationError as e:
            error_msg = e.messages[0] if hasattr(e, 'messages') else str(e)
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)})
