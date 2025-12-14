from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import extend_schema

from apps.operations.services import OrderFileAppService, OrderItemStatusAppService
from ..serializers import (
    DesignFileUploadSerializer,
    FileSerializer,
    OrderItemStatusUpdateSerializer,
    BaseOrderItemSerializer
)

# ========== Order Item Upload View ========== #
@extend_schema(tags=['Order-Upload-File'])
class OrderItemUploadView(GenericAPIView):
    """
    آپلود فایل طراحی جدید برای یک آیتم خاص.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DesignFileUploadSerializer

    def post(self, request, item_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = OrderFileAppService()
            new_file = service.upload_design_file(
                requester=request.user,
                item_id=item_id,
                file_data=serializer.validated_data['file'],
                requirement_id=serializer.validated_data['requirement_id']
            )
            
            return Response(
                FileSerializer(new_file, context={'request': request}).data, 
                status=status.HTTP_202_ACCEPTED
            )
            
        except (ValidationError, PermissionDenied) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "خطای سیستمی در آپلود فایل.", "error": str(e)}, status=500)

# ========== Order Item Status Update View ========== #
@extend_schema(tags=['Order-Item-Status'])
class OrderItemStatusUpdateView(GenericAPIView):
    """
    تغییر وضعیت فنی یک قلم سفارش (Item).
    مخصوص طراح، ناظر چاپ و QC.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemStatusUpdateSerializer

    def put(self, request, pk):
        """ pk: شناسه آیتم (OrderItem ID) """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = OrderItemStatusAppService()
            updated_item = service.change_item_status(
                requester=request.user,
                item_id=pk,
                new_status=serializer.validated_data['new_status'],
                admin_note=serializer.validated_data.get('admin_note')
            )
            
            return Response(
                BaseOrderItemSerializer(updated_item).data, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
