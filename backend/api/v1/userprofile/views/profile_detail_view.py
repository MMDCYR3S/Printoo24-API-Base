from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.userprofile.services import ProfileDetailService, UserFeedbackService
from ..serializers import CustomerProfileSerializer, ProfileCommentSerializer

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
        
    @extend_schema(
        summary="دریافت اطلاعات کامل پروفایل",
        description="این متد اطلاعات احراز هویت (User) را با اطلاعات تکمیلی (Profile) ترکیب کرده و برمی‌گرداند.",
        responses={200: CustomerProfileSerializer},
        examples=[
            OpenApiExample(
                'Full Profile Response',
                summary='نمونه پاسخ کامل',
                description='شامل نام کاربری، ایمیل و اطلاعات شخصی.',
                value={
                    "id": 1,
                    "username": "reza_ahmadi",
                    "email": "reza@example.com",
                    "is_active": True,
                    "first_name": "رضا",
                    "last_name": "احمدی",
                    "phone_number": "09121112233",
                    "company": "شرکت چاپ برتر",
                    "bio": "مدیر تدارکات",
                    "created_at": "2024-01-15T10:30:00Z"
                }
            )
        ]
    )
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
                'id': user.id,
                'phone_number': user.phone_number if user else '',
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                # ===== اطلاعات پروفایل ===== # 
                'first_name': profile.first_name if profile else '',
                'last_name': profile.last_name if profile else '',
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
            return Response({'detail': f'خطایی در دریافت اطلاعات رخ داد.{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="ویرایش پروفایل",
        description="فیلدهایی مثل `username` و `email` فقط خواندنی هستند و تغییر نمی‌کنند. فقط اطلاعات پروفایل (نام، شرکت و...) قابل ویرایش است.",
        request=CustomerProfileSerializer,
        responses={200: CustomerProfileSerializer},
        examples=[
            OpenApiExample(
                'Update Request',
                summary='درخواست ویرایش نام و شرکت',
                value={
                    "first_name": "محمد",
                    "last_name": "احمدی",
                    "company": "شرکت جدید",
                    "phone_number": "09120000000"
                },
                request_only=True
            )
        ]
    )
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
                    'phone_number': user.phone_number,
                    'first_name': profile.first_name,
                    'last_name': profile.last_name,
                    'company': profile.company,
                    'bio': profile.bio,
                    'msg': 'پروفایل با موفقیت بروزرسانی شد.'
                }
                return Response(response_data, status=status.HTTP_200_OK)
            
            except DjangoValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'detail': f'خطای سیستمی: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
# ===== User Comment List View ===== #
@extend_schema(tags=['Profile'])
class UserCommentListView(ListAPIView):
    """
    لیست تاریخچه نظرات کاربر
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileCommentSerializer

    @extend_schema(
        summary="لیست نظرات کاربر",
        examples=[
            OpenApiExample(
                'Comment History',
                summary='لیست نظرات',
                description='شامل یک نظر تایید شده و یک نظر در انتظار بررسی.',
                value=[
                    {
                        "id": 10,
                        "product_name": "کارت ویزیت لمینت",
                        "product_slug": "laminate-card",
                        "message": "کیفیت چاپ عالی بود، ممنون.",
                        "status": "approved",
                        "status_display": "تایید شده",
                        "admin_note": "",
                        "created_at": "2024-02-01T15:00:00Z"
                    },
                    {
                        "id": 12,
                        "product_name": "سربرگ A4",
                        "product_slug": "letterhead-a4",
                        "message": "آیا امکان تغییر رنگ وجود دارد؟",
                        "status": "pending",
                        "status_display": "در انتظار بررسی",
                        "admin_note": "در حال بررسی توسط واحد طراحی",
                        "created_at": "2024-02-05T09:00:00Z"
                    }
                ]
            )
        ]
    )
    def get_queryset(self):
        service = UserFeedbackService(user=self.request.user)
        return service.get_my_comments()            
