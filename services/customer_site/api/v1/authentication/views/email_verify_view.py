from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

from ..serializers import EmailVerificationSerializer
from apps.authentication.services import VerificationService,  TokenService
from core.common.users.user_services import UserService
from core.common.users.user_repo import UserRepository

# ========= Verify Email View ========= #
class VerifyEmailApiView(GenericAPIView):
    """
    ارسال کد تأیید و اعتبارسنجی آن توسط سیستم
    """
    
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer
    
    def post(self, request, *args, **kwargs):
        """
        دریافت کد تأیید توسط کاربر
        اگر که کد تایید درست باشه، کاربر توسط سرویس های مورد نظر،
        تایید میشه و کش هم پاک میشه. در غیر اینصورت، ارور مورد انتظار
        از طرف سیستم به کاربر نمایش داده میشه.
       *جهت بررسی منطق، باید به بخش سرویس ها رجوع کرد. 
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get("email")
        code = serializer.validated_data.get("code")
        
        # ===== ایجاد کانکشن با ریپازیتوری کاربر و سرویس ===== #
        user_repo = UserRepository()
        user_service = UserService(user_repo)
        verify_service = VerificationService(user_service=user_service)
        
        # ==== اعتبارسنجی کد تأیید و ایجاد توکن برای کاربر ===== #
        try:
            verified_user = verify_service.verify_code(email=email, code=code)
            tokens = TokenService.create_token_for_user(verified_user)
            
            return Response(tokens, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response({'error': e.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
            
