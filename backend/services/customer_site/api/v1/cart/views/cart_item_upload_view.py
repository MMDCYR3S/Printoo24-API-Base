from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiTypes, OpenApiExample

from ..serializers import CartItemFileUploadSerializer
from apps.cart.services import CartItemUploadService

# ===== Cart Item File Upload View ===== #
@extend_schema(tags=["Cart"])
class CartItemFileUploadView(GenericAPIView):
    """
    POST /api/v1/cart/items/{item_id}/upload/
    آپلود فایل برای یک آیتم خاص در سبد خرید.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemFileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        summary="آپلود فایل برای آیتم سبد",
        description="""
        فایل طراحی را برای یک آیتم خاص در سبد خرید آپلود می‌کند.
        
        **توجه:** این ریکوئست باید به صورت `multipart/form-data` ارسال شود.
        """,
        request=CartItemFileUploadSerializer,
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                'Upload Response Success',
                summary='پاسخ موفق آپلود',
                value={
                    "message": "فایل با موفقیت آپلود شد.",
                    "upload_id": 15,
                    "file_name": "design_front.pdf",
                    "requirement_id": 2
                },
                response_only=True,
                status_codes=[201]
            )
        ]
    )
    def post(self, request, item_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        requirement_id = serializer.validated_data['requirement_id']
        file_obj = serializer.validated_data['file']
        
        service = CartItemUploadService()
        
        try:
            # ===== فراخوانی سرویس و آپلود فایل ===== #
            upload_instance = service.upload_file(
                user=request.user,
                cart_item_id=item_id,
                requirement_id=requirement_id,
                file_obj=file_obj
            )
            
            return Response({
                "message": "فایل با موفقیت آپلود شد.",
                "upload_id": upload_instance.id,
                "file_name": upload_instance.file.name,
                "requirement_id": requirement_id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
