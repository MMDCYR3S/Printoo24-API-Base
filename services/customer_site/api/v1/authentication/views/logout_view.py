from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from ..serializers import LogoutSerializer
from apps.authentication.services import TokenService

# ========= Logout View ========= #
class LogoutAPIView(GenericAPIView):
    """
    پردازش درخواست خروج کاربر.
    refresh token را دریافت و آن را غیرفعال (blacklist) می‌کند.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        """ 
        با استفاده از متد POST، توکن رو به صورت خودکار
        از طرف کاربر دریافت می کند و اون رو به لیست سیاه
        انتقال میده.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        refresh_token = serializer.validated_data['refresh']
        
        # ===== انتقال توکن رفرش به لیست سیاه ===== #
        TokenService.send_to_blacklist(refresh_token)
        return Response(status=status.HTTP_204_NO_CONTENT)
