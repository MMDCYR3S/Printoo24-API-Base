from rest_framework.generics import GenericAPIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.operations.services import OrderTransitionAppService
from apps.order.domain_services import OrderStatusService
from apps.permissions import AppPermissionChecker
from ..serializers import (
    OrderStatusListSerializer, OrderStatusInputSerializer,
    OrderTransitionSerializer, OrderStatusSerializer
)

# ========== Order Status ViewSet ========== #
@extend_schema(tags=['Admin - Order Status'])
class OrderStatusViewSet(viewsets.ViewSet):
    """
    ViewSet برای مدیریت کامل CRUD وضعیت‌های سفارش (Status).
    """
    permission_classes = [IsAuthenticated]

    def get_service(self):
        return OrderStatusService()

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

# ========== Order Transition View ========== # 
@extend_schema(tags=['Admin - Order Status Transition'])
class OrderTransitionView(GenericAPIView):
    """
    تغییر وضعیت سفارش (سطح کل سفارش).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderTransitionSerializer

    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            service = OrderTransitionAppService()
            
            updated_order = service.execute_transition(
                requester=request.user,
                order_id=pk,
                new_status_code=data['new_status_code'],
                description=data.get('description')
            )
            
            return Response({
                "message": "وضعیت سفارش با موفقیت تغییر کرد.",
                "id": updated_order.id,
                "new_status": updated_order.current_status.name,
                "new_status_code": updated_order.current_status.internal_code
            }, status=status.HTTP_200_OK)
            
        except (ValidationError, PermissionDenied) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"detail": f"خطای سیستمی رخ داده است.{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
