from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from ..serializers import TemporaryFileUploadSerializer
from apps.cart.services import TemporaryFileService

@extend_schema(tags=["Cart"])
class TemporaryFileUploadView(GenericAPIView):
    """
    این API فایل را دریافت کرده، اعتبارسنجی فنی (DPI, CMYK, Size) انجام می‌دهد
    و در صورت تایید، نام فایل موقت (UUID) را برمی‌گرداند.
    POST /api/cart/upload-temporary-file/
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] 
    serializer_class = TemporaryFileUploadSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            # فراخوانی سرویس آپلود
            service = TemporaryFileService()
            
            temp_filename = service.upload_temp_file(
                uploaded_file=data['file'],
                product_id=data['product_id'],
                size_id=data.get('size_id'),
                custom_width=data.get('custom_width'),
                custom_height=data.get('custom_height')
            )
            
            return Response({
                "temp_file_name": temp_filename,
                "message": "فایل با موفقیت آپلود و تایید شد."
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            # خطاهای مربوط به اعتبارسنجی فایل (مثلا DPI پایین)
            return Response(
                {"error": e.detail if hasattr(e, 'detail') else str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            # خطاهای پیش‌بینی نشده سیستمی
            return Response(
                {"error": "خطای سیستمی در آپلود فایل.", "detail": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
