from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import extend_schema

from apps.operations.services import OrderFileAppService
from ..serializers import (
    DesignFileUploadSerializer, 
    FileReviewSerializer, 
    FileSerializer
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

@extend_schema(tags=['Order-Upload-File'], summary="تایید یا رد فایل طراحی")
class FileReviewView(GenericAPIView):
    """
    تغییر وضعیت تایید/رد یک فایل.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FileReviewSerializer

    def put(self, request, file_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = OrderFileAppService()
            updated_file = service.review_design_file(
                requester=request.user,
                file_id=file_id,
                is_accepted=serializer.validated_data['is_accepted'],
                feedback=serializer.validated_data.get('admin_feedback')
            )
            
            return Response(
                FileSerializer(updated_file, context={'request': request}).data,
                status=status.HTTP_200_OK
            )
            
        except (ValidationError, PermissionDenied) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
