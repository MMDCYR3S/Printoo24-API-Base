from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.core.exceptions import ValidationError, PermissionDenied
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiTypes

from apps.accounts.services import StaffAppService
from ..serializers import (
    StaffListSerializer, StaffCreateSerializer, StaffUpdateSerializer,
    BulkIdsSerializer, BulkRoleChangeSerializer
)
from core.users.exceptions import UsernameAlreadyExistsException, EmailAlreadyExistsException

# ========== STAFF MANAGEMENT VIEWS ========== #
@extend_schema(tags=["Users-Staffs"])
class StaffListCreateView(GenericAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = StaffAppService()

    @extend_schema(
        summary="لیست تمام پرسنل",
        description="لیست کاربرانی که دارای نقش سیستمی (غیر از مشتری عادی) هستند.",
        responses={200: StaffListSerializer(many=True)}
    )
    def get(self, request):
        """ لیست تمام پرسنل """
        try:
            staff_list = self.service.get_staff_list(request.user)
            serializer = StaffListSerializer(staff_list, many=True)
            return Response(serializer.data)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

    @extend_schema(
        summary="استخدام کارمند جدید",
        description="""
        ایجاد یک کاربر جدید و انتساب مستقیم نقش به او.
        
        **نکات مهم:**
        * `role_id`: شناسه نقشی که قبلاً ساخته‌اید.
        * `password`: باید حداقل ۸ کاراکتر باشد.
        """,
        request=StaffCreateSerializer,
        responses={
            201: StaffListSerializer,
            409: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                'New Staff Example',
                summary='مثال ثبت نام حسابدار',
                value={
                    "username": "ahmad_accountant",
                    "email": "ahmad@company.com",
                    "password": "StrongPassword123!",
                    "role_id": 2
                },
                request_only=True
            ),
            OpenApiExample(
                'Conflict Error',
                summary='خطای تکراری بودن کاربر (409)',
                value={"detail": "کاربری با این نام کاربری وجود دارد."},
                response_only=True,
                status_codes=[409]
            )
        ]
    )
    def post(self, request):
        """ استخدام کارمند جدید """
        serializer = StaffCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = self.service.create_staff(request.user, serializer.validated_data)
                return Response(StaffListSerializer(user).data, status=status.HTTP_201_CREATED)
            
            except (UsernameAlreadyExistsException, EmailAlreadyExistsException) as e:
                return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
            except ValidationError as e:
                return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
            except PermissionDenied as e:
                return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ========== STAFF DETAIL VIEW ========== #
@extend_schema(tags=["Users-Staffs"])
class StaffDetailView(GenericAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = StaffAppService()

    @extend_schema(
        summary="ویرایش اطلاعات کارمند",
        description="می‌توانید نقش، ایمیل یا وضعیت فعال بودن کاربر را تغییر دهید.",
        request=StaffUpdateSerializer,
        responses={200: StaffListSerializer},
        examples=[
            OpenApiExample(
                'Update Role Example',
                summary='تغییر نقش به مدیر فروش',
                value={
                    "role_id": 5,
                    "is_active": True
                }
            )
        ]
    )
    def put(self, request, pk):
        """ ویرایش کارمند """
        serializer = StaffUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = self.service.update_staff(request.user, pk, serializer.validated_data)
                return Response(StaffListSerializer(user).data)
            except ValidationError as e:
                return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
            except PermissionDenied as e:
                return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """ اخراج (حذف) کارمند """
        try:
            self.service.delete_staff(request.user, pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)



# ========== BULK ACTION VIEWS ========== #
@extend_schema(tags=["Users-Staffs"])
class StaffBulkActionsView(GenericAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = StaffAppService()

    @extend_schema(
        summary="عملیات گروهی روی پرسنل",
        description="""
        انجام عملیات روی چندین کاربر به صورت همزمان.
        
        **لیست Action های مجاز در URL:**
        * `delete`: حذف گروهی
        * `activate`: فعال‌سازی گروهی
        * `deactivate`: غیرفعال‌سازی گروهی
        * `change_role`: تغییر نقش گروهی
        
        **توجه:** ساختار Body بر اساس Action تغییر می‌کند (به مثال‌ها دقت کنید).
        """,
        parameters=[
            OpenApiParameter(
                name='action',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='نوع عملیات',
                enum=['delete', 'activate', 'deactivate', 'change_role']
            )
        ],
        # نکته: چون بادی متغیر است، از آبجکت کلی استفاده می‌کنیم و با مثال توضیح می‌دهیم
        request=OpenApiTypes.OBJECT, 
        responses={200: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Bulk Delete/Activate',
                summary='مثال برای حذف/فعال‌سازی',
                description='برای اکشن‌های delete, activate, deactivate فقط لیست ID ارسال کنید.',
                value={
                    "ids": [10, 12, 15]
                },
                request_only=True
            ),
            OpenApiExample(
                'Bulk Change Role',
                summary='مثال برای تغییر نقش (Change Role)',
                description='برای اکشن change_role باید شناسه نقش جدید را هم بفرستید.',
                value={
                    "ids": [10, 12, 15],
                    "new_role_id": 3
                },
                request_only=True
            )
        ]
    )
    def post(self, request, action):
        """
        مدیریت عملیات گروهی بر اساس پارامتر action در URL.
        actions: delete, activate, deactivate, change_role
        """
        try:
            if action == 'delete':
                serializer = BulkIdsSerializer(data=request.data)
                if serializer.is_valid():
                    result = self.service.bulk_delete(request.user, serializer.validated_data['ids'])
                    return Response(result)

            elif action == 'activate':
                serializer = BulkIdsSerializer(data=request.data)
                if serializer.is_valid():
                    count = self.service.bulk_toggle_active(request.user, serializer.validated_data['ids'], True)
                    return Response({"updated_count": count})

            elif action == 'deactivate':
                serializer = BulkIdsSerializer(data=request.data)
                if serializer.is_valid():
                    count = self.service.bulk_toggle_active(request.user, serializer.validated_data['ids'], False)
                    return Response({"updated_count": count})

            elif action == 'change_role':
                serializer = BulkRoleChangeSerializer(data=request.data)
                if serializer.is_valid():
                    count = self.service.bulk_change_role(
                        request.user, 
                        serializer.validated_data['ids'], 
                        serializer.validated_data['new_role_id']
                    )
                    return Response({"updated_count": count})
            
            else:
                return Response({"detail": "اکشن نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)

