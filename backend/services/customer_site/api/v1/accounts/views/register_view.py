from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from ..serializers import RegisterSerializer
from apps.accounts.services import AuthService

# ======= Register API View ======= #
@extend_schema(tags=['Accounts'])
class RegisterAPIView(APIView):
    """
    ویوی ثبت نام کاربر
    با بهره گیری از ریپازیتوری و سرویس های مرتبط با کاربر، این ویو
    نقش یک انتقال دهنده و همچنین هماهنگ کننده را بازی می کندو فقط از
    متدهای مورد نظر برای ایجاد کاربر بهره می برد.
    """
    
    permission_classes = [AllowAny]
    
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
                "message" : "ثبت نام با موفقیت انجام شد.", "username" : registered_user.username
            }, status=status.HTTP_201_CREATED)
