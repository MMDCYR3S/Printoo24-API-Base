from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError

from core.domain.commerce.order import OrderStatusGroupDomainService
from apps.permissions import AppPermissionChecker
from ..serializers import OrderStatusGroupListSerializer, OrderStatusGroupInputSerializer

# ========== Order Status Group ViewSet ========== #
@extend_schema(tags=['Admin-StatusGroups'])
class OrderStatusGroupViewSet(viewsets.ViewSet):
    """
    ViewSet برای مدیریت کامل CRUD گروه‌های وضعیت سفارش.
    """
    permission_classes = [IsAuthenticated]

    def get_service(self):
        return OrderStatusGroupDomainService()

    def check_object_permissions(self, action_name):
        """ اعمال AppPermissionChecker بر اساس نوع عملیات """
        AppPermissionChecker.check_has_permission(
            self.request.user, 
            f'change_orderstatusgroup' if action_name == 'update' else f'{action_name}_orderstatusgroup'
        )

    def list(self, request):
        """ نمایش لیست گروه‌های وضعیت همراه با تعداد Status‌های وابسته. """
        self.check_object_permissions('view')
        service = self.get_service()
        queryset = service.repo.get_all_groups_with_status_count()
        serializer = OrderStatusGroupListSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """ ایجاد یک گروه وضعیت جدید. """
        self.check_object_permissions('add')
        serializer = OrderStatusGroupInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            group = self.get_service().create_group(serializer.validated_data)
            return Response(OrderStatusGroupListSerializer(group).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """ نمایش جزئیات گروه وضعیت. """
        self.check_object_permissions('view')
        group = self.get_service().repo.get_by_id(pk)
        if not group:
            return Response({"detail": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderStatusGroupListSerializer(group).data)

    def update(self, request, pk=None):
        """ ویرایش گروه وضعیت. """
        self.check_object_permissions('update')
        serializer = OrderStatusGroupInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            group = self.get_service().update_group(pk, serializer.validated_data)
            return Response(OrderStatusGroupListSerializer(group).data)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """ حذف گروه وضعیت. """
        self.check_object_permissions('delete')
        try:
            self.get_service().delete_group(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
