from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.views import extend_schema

from apps.operations.services import OrderFileAppService
from ..serializers import DesignFileUploadSerializer, FileStatusChangeSerializer, FileSerializer

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
        if serializer.is_valid():
            service = OrderFileAppService()
            try:
                new_file = service.upload_design_file(
                    requester=request.user,
                    item_id=item_id,
                    file_data=serializer.validated_data['file'],
                    requirement_id=serializer.validated_data['requirement_id']
                )
                return Response(FileSerializer(new_file).data, status=status.HTTP_202_ACCEPTED)
            except (ValidationError, PermissionDenied) as e:
                return Response({"detail": str(e)}, status=400)
        
        return Response(serializer.errors, status=400)

# ========== File Status View ========== #
@extend_schema(tags=['Order-Upload-File'])
class FileStatusView(GenericAPIView):
    """
    تغییر وضعیت یک فایل (تایید/رد).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FileStatusChangeSerializer

    def put(self, request, file_id):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            service = OrderFileAppService()
            try:
                updated_file = service.change_file_status(
                    requester=request.user,
                    file_id=file_id,
                    new_status=serializer.validated_data['status'],
                    feedback=serializer.validated_data.get('admin_feedback')
                )
                return Response(FileSerializer(updated_file).data)
            except (ValidationError, PermissionDenied) as e:
                return Response({"detail": str(e)}, status=400)
        
        return Response(serializer.errors, status=400)
