import uuid
import os

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from drf_spectacular.views import extend_schema

from ..serializers import TemporaryFileUploadSerializer

# ======== Temporary File Upload View ======== #
@extend_schema(tags=["Cart"])
class TemporaryFileUploadView(GenericAPIView):
    """
    این API یک فایل را دریافت کرده، آن را در یک پوشه موقت ذخیره می‌کند
    و نام فایل تولید شده (UUID) را برمی‌گرداند.
    POST /api/cart/upload-temporary-file/
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser,]
    serializer_class = TemporaryFileUploadSerializer
    
    def post(self, request, *args, **kwargs):
        """
        اعتبارسنجی، ساخت سرویس های مورد نظر و آپلود فایل های موقت
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            uploaded_file = serializer.validated_data["file"]
            
            # ===== ساخت مسیر موقت برای ذخیره سازی ===== #
            original_extensions = os.path.splitext(uploaded_file.name)[1]
            temp_filename = f"{uuid.uuid4()}{original_extensions}"
            temp_path = os.path.join("uploads", "temp", temp_filename)
            # ===== ذخیره سازی فایل در مسیر انتخاب شده برای جنگو ===== #
            default_storage.save(temp_path, uploaded_file)
            
            return Response({
                "temp_file_name" : temp_filename
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
