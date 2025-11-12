from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer
from .services import RegistrationService
from shared_libs.core.common.users.user_services import UserService
from shared_libs.core.common.users.user_repo import UserRepository

# ======= Register API View ======= #
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
        
        # ====== ایجاد کاربر ====== #
        user_repo = UserRepository()
        user_service = UserService(repository=user_repo)
        registration_service = RegistrationService(user_service=user_service)
        
        # ====== ثبت نام کاربر با استفاده از سریالایزر و ریپازیتوری مورد نظر ====== #
        registered_user = registration_service.register_user(serializer.validated_data)
        
        return Response({
                "message" : "ثبت نام با موفقیت انجام شد.", "username" : registered_user.username
            }, status=status.HTTP_201_CREATED)
