from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.views import extend_schema

from apps.userprofile.services import ProfileDetailService
from ..serializers import CustomerProfileSerializer 

# ===== Customer Profile API View ===== #
@extend_schema(tags=["Profile"])
class CustomerProfileAPIView(APIView):
    """
    API برای دریافت و ویرایش پروفایل کاربر جاری
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ===== تزریق وابستگی ===== #
        self._service = ProfileDetailService()
        
    def get(self, request):
        """
        دریافت اطلاعات پروفایل کاربر
        """
        try:
            # ===== ایجاد سرویس برای دریافت اطلاعات ===== #
            data_bundle = self._service.get_profile_detail(request.user.id)
            # ===== دریافت اطلاعات کاربر و پروفایل ===== #
            user = data_bundle['user']
            profile = data_bundle['profile']
            
            combined_data = {
                # ===== اطلاعات کاربر ===== #
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                # ===== اطلاعات پروفایل ===== # 
                'first_name': profile.first_name if profile else '',
                'last_name': profile.last_name if profile else '',
                'phone_number': profile.phone_number if profile else '',
                'company': profile.company if profile else '',
                'bio': profile.bio if profile else '',
                'created_at': profile.created_at if profile else user.created_at,
            }
            # ===== سریالایزر کردن اطلاعات ===== #
            serializer = CustomerProfileSerializer(instance=combined_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except DjangoValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': 'خطایی در دریافت اطلاعات رخ داد.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        """
        ویرایش کامل یا جزئی پروفایل کاربر
        """
        # ===== اعتبارسنجی اطلاعات از طریق سریالایزر ===== #
        serializer = CustomerProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # ===== ایجاد سرویس برای ویرایش پروفایل ===== #
                updated_data_bundle = self._service.update_profile(
                    user_id=request.user.id, 
                    data=serializer.validated_data
                )
                
                # ===== آماده سازی اطلاعاتک کاربر ===== #
                user = updated_data_bundle['user']
                profile = updated_data_bundle['profile']
                
                # ===== ارسال پاسخ ===== #
                response_data = {
                    'username': user.username,
                    'email': user.email,
                    'first_name': profile.first_name,
                    'last_name': profile.last_name,
                    'phone_number': profile.phone_number,
                    'company': profile.company,
                    'bio': profile.bio,
                    'msg': _('پروفایل با موفقیت بروزرسانی شد.')
                }
                return Response(response_data, status=status.HTTP_200_OK)
            
            except DjangoValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'detail': f'خطای سیستمی: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            