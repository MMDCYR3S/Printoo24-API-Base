from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.models import Permission
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes

# ===== سرویس‌ها (فرض بر وجود داشتن) ===== #
from core.models import AccessScope
from apps.accounts.services import RoleAppService 
from ..serializers import (
    RoleOutputSerializer, RoleInputSerializer, PermissionSerializer,
    StaffListSerializer, StaffCreateSerializer, StaffUpdateSerializer,
    BulkIdsSerializer, BulkRoleChangeSerializer, AccessScopeSerializer
)

# ========== PERMISSIONS ========== #
@extend_schema(tags=["Users-Roles"])
class PermissionListAPIView(GenericAPIView):
    """
    لیست تمام مجوزهای سیستمی (Permissions).
    این لیست برای پر کردن چک‌باکس‌ها در فرم 'ایجاد نقش' استفاده می‌شود.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = PermissionSerializer

    @extend_schema(
        summary="دریافت لیست کل مجوزهای سیستم",
        responses={200: PermissionSerializer(many=True)}
    )
    def get(self, request):
        """ دریافت لیست کل مجوزهای سیستم  """
        permissions = Permission.objects.exclude(content_type__app_label__in=['admin', 'contenttypes', 'sessions'])
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)

# ========== Access Scope API View ========== #
@extend_schema(tags=["Users-Roles"])
class AccessScopeListAPIView(GenericAPIView):
    """
    لیست تمام محدوده‌های دسترسی (Scopes) تعریف شده در سیستم.
    مثال: 'workshop_access', 'financial_read', ...
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AccessScopeSerializer

    @extend_schema(
        summary="دریافت لیست محدوده‌های دسترسی (Scopes)",
        responses={200: AccessScopeSerializer(many=True)}
    )
    def get(self, request):
        scopes = AccessScope.objects.all()
        serializer = self.get_serializer(scopes, many=True)
        return Response(serializer.data)

# ========== ROLE MANAGEMENT VIEWS ========== #
@extend_schema(tags=["Users-Roles"])
class RoleListCreateView(GenericAPIView):
    """
    مدیریت نقش‌های کاربری.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RoleInputSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = RoleAppService()

    @extend_schema(
        summary="لیست نقش‌ها",
        responses={200: RoleOutputSerializer(many=True)}
    )
    def get(self, request):
        roles = self.service.get_role_list(request.user)
        return Response(RoleOutputSerializer(roles, many=True).data)

    @extend_schema(
        summary="ایجاد نقش جدید",
        request=RoleInputSerializer,
        responses={201: RoleOutputSerializer},
        examples=[
            OpenApiExample(
                'Custom Scope Role',
                summary='نقش با اسکوپ‌های انتخابی',
                value={
                    "name": "مدیر انبار",
                    "slug": "inventory_manager",
                    "type": "admin",
                    "description": "دسترسی به اسکوپ انبار",
                    "permissions": [10, 20],
                    "scope_ids": [1, 2, 5], # <--- ارسال دستی اسکوپ‌ها
                    "is_customer": False
                }
            )
        ]
    )
    def post(self, request):
        serializer = RoleInputSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # داده‌های validated شامل type و permissions هستند
                role = self.service.create_role(request.user, serializer.validated_data)
                return Response(RoleOutputSerializer(role).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
            except PermissionDenied as e:
                return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Users-Roles"])
class RoleDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoleInputSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = RoleAppService()

    @extend_schema(
        summary="ویرایش نقش",
        description="با تغییر `type`، دسترسی‌های Scope نقش به صورت خودکار بازنشانی می‌شوند.",
        request=RoleInputSerializer,
        responses={200: RoleOutputSerializer}
    )
    def put(self, request, pk):
        serializer = RoleInputSerializer(data=request.data)
        if serializer.is_valid():
            try:
                role = self.service.update_role(request.user, pk, serializer.validated_data)
                return Response(RoleOutputSerializer(role).data)
            except ValidationError as e:
                return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
            except PermissionDenied as e:
                return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="حذف نقش")
    def delete(self, request, pk):
        try:
            self.service.delete_role(request.user, pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
