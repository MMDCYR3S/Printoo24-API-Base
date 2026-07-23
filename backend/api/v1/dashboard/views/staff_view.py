from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.core.exceptions import ValidationError, PermissionDenied

from core.users.exceptions import EmailAlreadyExistsException, UsernameAlreadyExistsException

from apps.dashboard.services import StaffDashboardService
from ..serializers import (
    StaffSerializer, 
    StaffCreateSerializer, 
    StaffUpdateSerializer,
    BulkIdsSerializer,
    BulkToggleStatusSerializer,
    BulkChangeRoleSerializer,
    RoleSerializer
)
from core.models import Role

# ===== Staff Management ViewSet ===== #
@extend_schema(tags=["Admin - Staff Management"])
class StaffViewSet(viewsets.ViewSet):
    """
    مدیریت پرسنل و ادمین‌ها.
    پشتیبانی از عملیات تکی و گروهی (تغییر وضعیت، حذف، تغییر نقش).
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = StaffDashboardService()

    # ===== 1. LIST ===== #
    @extend_schema(summary="لیست کارمندان", responses=StaffSerializer(many=True))
    def list(self, request):
        queryset = self.service.get_staff_list()
        serializer = StaffSerializer(queryset, many=True)
        return Response(serializer.data)

    # ===== 2. RETRIEVE ===== #
    @extend_schema(summary="جزئیات کارمند", responses=StaffSerializer)
    def retrieve(self, request, pk=None):
        try:
            user = self.service.get_staff_detail(pk)
            return Response(StaffSerializer(user).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ===== 3. CREATE ===== #
    @extend_schema(
        summary="ایجاد کارمند جدید",
        request=StaffCreateSerializer,
        responses={201: StaffSerializer},
        examples=[
            OpenApiExample(
                "ایجاد کارمند",
                value={
                    "phone_number": "09137555555",
                    "email": "ali@printoo.ir",
                    "password": "StrongPassword123!",
                    "role_id": 2
                },
                request_only=True
            )
        ]
    )
    def create(self, request):
        serializer = StaffCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = self.service.create_staff(serializer.validated_data)
            return Response(StaffSerializer(user).data, status=status.HTTP_201_CREATED)
        except (EmailAlreadyExistsException, UsernameAlreadyExistsException, ValidationError) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== 4. UPDATE ===== #
    @extend_schema(
        summary="ویرایش کارمند",
        request=StaffUpdateSerializer,
        responses={200: StaffSerializer},
        examples=[
            OpenApiExample(
                "ویرایش نقش و وضعیت",
                value={"role_id": 3, "is_active": False},
                request_only=True
            )
        ]
    )
    def partial_update(self, request, pk=None):
        serializer = StaffUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = self.service.update_staff(pk, serializer.validated_data)
            return Response(StaffSerializer(user).data)
        except (EmailAlreadyExistsException, UsernameAlreadyExistsException, ValidationError) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== 5. DELETE ===== #
    @extend_schema(summary="حذف کارمند")
    def destroy(self, request, pk=None):
        try:
            self.service.delete_staff(pk)
            return Response({"detail": "کارمند با موفقیت حذف شد."}, status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== 6. BULK DELETE ===== #
    @extend_schema(
        summary="حذف گروهی کارمندان",
        request=BulkIdsSerializer,
        examples=[OpenApiExample("حذف چند نفر", value={"user_ids": [10, 11, 15]})]
    )
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        serializer = BulkIdsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = self.service.bulk_delete(serializer.validated_data['user_ids'])
        return Response(result, status=status.HTTP_200_OK)

    # ===== 7. BULK TOGGLE STATUS ===== #
    @extend_schema(
        summary="فعال/غیرفعال‌سازی گروهی",
        request=BulkToggleStatusSerializer,
        examples=[OpenApiExample("غیرفعال سازی گروهی", value={"user_ids": [10, 11], "is_active": False})]
    )
    @action(detail=False, methods=['post'], url_path='bulk-toggle-status')
    def bulk_toggle_status(self, request):
        serializer = BulkToggleStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        updated_count = self.service.bulk_toggle_status(data['user_ids'], data['is_active'])
        return Response({"detail": f"وضعیت {updated_count} کاربر تغییر یافت."})

    # ===== 8. BULK CHANGE ROLE ===== #
    @extend_schema(
        summary="تغییر نقش گروهی",
        request=BulkChangeRoleSerializer,
        examples=[OpenApiExample("تغییر نقش دسته‌جمعی", value={"user_ids": [10, 11], "role_id": 4})]
    )
    @action(detail=False, methods=['post'], url_path='bulk-change-role')
    def bulk_change_role(self, request):
        serializer = BulkChangeRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        try:
            updated_count = self.service.bulk_change_role(data['user_ids'], data['role_id'])
            return Response({"detail": f"نقش {updated_count} کاربر تغییر یافت."})
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="لیست نقش‌ها",
        request=RoleSerializer,
    )
    @action(detail=False, methods=['get'], url_path='roles')
    def roles(self, request):
        try:
            role_list = Role.objects.filter(is_customer=False)
            serializer = RoleSerializer(role_list, many=True)
            return Response(serializer.data)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
