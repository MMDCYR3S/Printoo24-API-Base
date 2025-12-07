from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView 
from drf_spectacular.views import extend_schema

from apps.accounts.services import AuthAppService
from ..serializers import LoginSerializer, RefreshTokenSerializer

# ===== Staff Login View ===== #
@extend_schema(tags=['Accounts'])
class StaffLoginView(GenericAPIView):
    """
    ورود پرسنل به پنل مدیریت.
    """
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            service = AuthAppService()
            result = service.login_staff(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ===== Staff Logout View ===== #
@extend_schema(tags=['Accounts'])
class StaffLogoutView(GenericAPIView):
    """
    خروج (Blacklist کردن Refresh Token).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RefreshTokenSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            service = AuthAppService()
            service.logout(serializer.validated_data['refresh'])
            return Response({"detail": "با موفقیت خارج شدید."}, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
