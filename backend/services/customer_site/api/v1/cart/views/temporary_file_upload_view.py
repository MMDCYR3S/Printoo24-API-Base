from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.views import extend_schema

from ..serializers import TemporaryFileUploadSerializer
from apps.cart.services import TemporaryFileService

# ======== Temporary File Upload View ======== #
@extend_schema(tags=["Cart"])
class TemporaryFileUploadView(GenericAPIView):
    """
    این API یک فایل را دریافت کرده، آن را در یک پوشه موقت ذخیره می‌کند
    و نام فایل تولید شده (UUID) را برمی‌گرداند.
    POST /api/cart/upload-temporary-file/
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] 
    serializer_class = TemporaryFileUploadSerializer
    
    def post(self, request, *args, **kwargs):
        """
        اعتبارسنجی، ساخت سرویس های مورد نظر و آپلود فایل های موقت
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # ===== اعتبارسنجی داده ها از طرف سریالایزر ===== #
            data = serializer.validated_data
            
            service = TemporaryFileService()
            temp_filename = service.upload_temp_file(
                uploaded_file=data['file'],
                product_id=data['product_id'],
                size_id=data['size_id'],
                custom_width=data['custom_width'],
                custom_height=data['custom_height']
            )
            
            return Response({
                "temp_file_name" : temp_filename,
                "message": "فایل با موفقیت آپلود و اعتبارسنجی شد."
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
