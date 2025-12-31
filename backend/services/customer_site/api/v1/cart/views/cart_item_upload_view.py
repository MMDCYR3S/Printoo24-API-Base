from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiTypes

from ..serializers import CartItemFileUploadSerializer
from apps.cart.services import CartItemUploadService

# ===== Cart Item File Upload View ===== #
@extend_schema(tags=["Cart"])
class CartItemFileUploadView(GenericAPIView):
    """
    POST /api/v1/cart/items/{item_id}/upload/
    """
    permission_classes = [AllowAny]
    serializer_class = CartItemFileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        summary="آپلود فایل طراحی",
        description="ارسال فایل بصورت multipart/form-data. هدر X-Guest-Token برای مهمان الزامی است.",
        request=CartItemFileUploadSerializer,
        responses={201: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
    )
    def post(self, request, item_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # ===== دریافت دیتا ===== #
        requirement_id = serializer.validated_data.get('requirement_id') 
        file_obj = serializer.validated_data['file']
        
        # ===== استخراج شناسه کاربر و مهمان ===== #
        user = request.user if request.user.is_authenticated else None
        session_key = request.headers.get('X-Guest-Token')
        
        try:
            # ===== اجرا سرویس ===== #
            service = CartItemUploadService()
            upload_instance = service.upload_file(
                cart_item_id=item_id,
                file_obj=file_obj,
                user=user,
                session_key=session_key
            )
            
            return Response({
                "message": "فایل با موفقیت آپلود شد.",
                "upload_id": upload_instance.id,
                "file_name": upload_instance.file.name
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
