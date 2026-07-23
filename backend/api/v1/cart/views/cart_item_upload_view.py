from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiTypes, OpenApiExample

from ..serializers import CartItemFileUploadSerializer
from apps.cart.services import CartItemUploadService
from core.infrastructure.messages import msg_provider

# ========== FILE UPLOAD VIEW ========== #
@extend_schema(tags=["Cart"])
class CartItemFileUploadView(GenericAPIView):
    """
    POST /api/v1/cart/items/{item_id}/upload/
    آپلود فایل برای آیتم سبد خرید.
    """
    permission_classes = [AllowAny]
    serializer_class = CartItemFileUploadSerializer
    # ===== 
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @extend_schema(
        summary="آپلود فایل طراحی",
        description="""
        فایل را به صورت `multipart/form-data` ارسال کنید.
        سیستم به طور خودکار کاربر لاگین شده یا مهمان (از طریق کوکی Session) را شناسایی می‌کند.
        """,
        request=CartItemFileUploadSerializer,
        responses={
            201: OpenApiTypes.OBJECT, 
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                'Upload Success',
                summary='نمونه پاسخ موفق',
                value={
                    "message": "فایل با موفقیت آپلود شد.",
                    "upload_id": 15,
                    "file_name": "design.pdf"
                },
                response_only=True,
                status_codes=[201]
            )
        ]
    )
    def post(self, request, item_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        requirement_id = serializer.validated_data.get('requirement_id')
        file_obj = serializer.validated_data['file']
        
        # ===== تشخیص هویت (User یا Session) ===== #
        user = request.user if request.user.is_authenticated else None

        session_key = request.session.session_key
        
        service = CartItemUploadService()
        
        try:
            upload_instance = service.upload_file(
                cart_item_id=item_id,
                file_obj=file_obj,
                user=user,
                session_key=session_key
            )
            
            return Response({
                "message": msg_provider.get("cart.S4003"),
                "upload_id": upload_instance.id,
                "file_name": upload_instance.file.name,
                "requirement_id": requirement_id
            }, status=status.HTTP_201_CREATED)
            
        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ========== FILE DELETE VIEW ========== #
@extend_schema(tags=["Cart"])
class CartItemFileDeleteView(GenericAPIView):
    """
    DELETE /api/v1/cart/uploads/{upload_id}/
    حذف فایل آپلود شده از سبد خرید.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="حذف فایل طراحی",
        description="""
        با ارسال شناسه فایل (upload_id)، آن را از سبد خرید حذف می‌کند.
        سیستم به صورت خودکار چک می‌کند که فایل متعلق به کاربر (یا مهمان) فعلی باشد.
        """,
        responses={
            204: OpenApiTypes.OBJECT, 
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT
        }
    )
    def delete(self, request, upload_id):
        # ===== تشخیص هویت (User یا Session) ===== #
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key

        service = CartItemUploadService()
        
        try:
            service.delete_file(
                upload_id=upload_id,
                user=user,
                session_key=session_key
            )
            # در REST استاندارد، کد 204 برای حذف موفق برگردانده می‌شود
            return Response(
                {"message": msg_provider.get("cart.S4004")}, 
                status=status.HTTP_204_NO_CONTENT
            )
            
        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
