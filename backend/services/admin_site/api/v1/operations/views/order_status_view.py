# در فایل: services/admin_site/apps/operations/api/v1/status_groups/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from core.domain.commerce.order import OrderStatusDomainService
from apps.permissions import AppPermissionChecker
from ..serializers import OrderStatusListSerializer, OrderStatusInputSerializer

# ========== Order Status ViewSet ========== #
@extend_schema(tags=['Admin - Order Status'])
class OrderStatusViewSet(viewsets.ViewSet):
    """
    ViewSet برای مدیریت کامل CRUD وضعیت‌های سفارش (Status).
    """
    permission_classes = [IsAuthenticated]

    def get_service(self):
        return OrderStatusDomainService()

    def check_object_permissions(self, action_name):
        """ اعمال AppPermissionChecker بر اساس نوع عملیات """
        AppPermissionChecker.check_has_permission(
            self.request.user, 
            f'change_orderstatus' if action_name == 'update' else f'{action_name}_orderstatus'
        )

    def list(self, request):
        """ نمایش لیست وضعیت‌های سفارش همراه با گروه مرتبط. """
        self.check_object_permissions('view')
        
        service = self.get_service()
        queryset = service.repo.get_all_statuses_with_details()
        serializer = OrderStatusListSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """ ایجاد یک وضعیت جدید. """
        self.check_object_permissions('add')
        
        serializer = OrderStatusInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            status_obj = self.get_service().create_status(serializer.validated_data)
            return Response(OrderStatusListSerializer(status_obj).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """ نمایش جزئیات گروه وضعیت. """
        self.check_object_permissions('view')
        status = self.get_service().repo.get_by_id(pk)
        if not status:
            return Response({"detail": "Status not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderStatusListSerializer(status).data)

    def update(self, request, pk=None):
        """ ویرایش گروه وضعیت. """
        self.check_object_permissions('update')
        serializer = OrderStatusInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            status = self.get_service().update_status(pk, serializer.validated_data)
            return Response(OrderStatusInputSerializer(status).data)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """ حذف گروه وضعیت. """
        self.check_object_permissions('delete')
        try:
            self.get_service().delete_status(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    