from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema

from apps.dashboard.services import CartDashboardService, CartFileService
from ..serializers import (
    UserCartDetailSerializer, 
    CartItemAddSimpleSerializer, 
    CartItemUpdateSerializer,
    CartListSerializer,
    CartFileUploadSerializer,
)

# ===== Cart Dashboard View Set ===== #
@extend_schema(tags=['Dashboard-Cart'])
class CartDashboardViewSet(viewsets.ViewSet):
    """
    مدیریت سبد خرید کاربران توسط ادمین.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CartDashboardService()

    # ===== مشاهده سبد خرید کاربر ===== #
    @extend_schema(responses=UserCartDetailSerializer)
    def retrieve(self, request, pk=None):
        """ 
        دریافت سبد خرید یک کاربر.
        توجه: pk در اینجا user_id است.
        """
        data = self.service.get_user_cart_details(user_id=pk)
        serializer = UserCartDetailSerializer(data['cart'])
        return Response(serializer.data)

    # ===== خالی کردن سبد ===== #
    @extend_schema(summary="حذف کل سبد خرید کاربر")
    def destroy(self, request, pk=None):
        """ pk = user_id """
        self.service.clear_user_cart(user_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== افزودن آیتم به سبد کاربر ===== #
    @extend_schema(
        request=CartItemAddSimpleSerializer, 
        summary="افزودن آیتم برای کاربر (فرمت ساده)",
        description="استفاده از slug محصول و ID ویژگی‌ها"
    )
    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
        """ pk = user_id """
        serializer = CartItemAddSimpleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.service.add_item_to_user_cart_simple(
                user_id=pk, 
                data=serializer.validated_data
            )
            
            # ===== مشاهده سبد ===== #
            data = self.service.get_user_cart_details(user_id=pk)
            return Response(UserCartDetailSerializer(data['cart']).data, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({'detail': e.messages if hasattr(e, 'messages') else str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=CartItemUpdateSerializer, summary="ویرایش آیتم سبد")
    @action(detail=True, methods=['patch'], url_path='items/(?P<item_id>\d+)')
    def update_item(self, request, pk=None, item_id=None):
        """ pk = user_id, item_id = cart_item.id """
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.service.update_cart_item(
            user_id=pk, 
            item_id=item_id, 
            data=serializer.validated_data
        )
        return Response({'status': 'Item updated'})

    @extend_schema(summary="حذف آیتم از سبد")
    @action(detail=True, methods=['delete'], url_path='items/(?P<item_id>\d+)')
    def remove_item(self, request, pk=None, item_id=None):
        self.service.remove_item_from_cart(user_id=pk, item_id=item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # ===== مشاهده لیست تمام سبدها ===== #
    @extend_schema(responses=CartListSerializer(many=True))
    def list(self, request):
        """
        لیست تمام سبدهای خرید فعال (غیر خالی) کاربران.
        """
        queryset = self.service.get_all_carts_queryset()
        serializer = CartListSerializer(queryset, many=True)
        return Response(serializer.data)
    
# ===== Cart File Upload View Set ===== #
@extend_schema(tags=['Dashboard-Cart'])
class CartFileUploadViewSet(viewsets.ViewSet):
    """
    مدیریت آپلود فایل‌های طراحی توسط کاربر.
    """
    
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CartFileService()

    @extend_schema(summary="آپلود فایل طراحی برای آیتم سبد خرید", request=CartFileUploadSerializer)
    @action(detail=True, methods=['post'], url_path='upload')
    def upload_for_item(self, request, pk=None):
        """
        pk: شناسه آیتم سبد خرید (CartItem ID).
        """
        serializer = CartFileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file_obj = serializer.validated_data['file']
        requirement_id = serializer.validated_data['requirement_id']
        
        result = self.service.upload_file_async(
            cart_item_id=pk,
            requirement_id=requirement_id,
            file_obj=file_obj
        )

        if result['status'] == 'processing':
            return Response(result, status=status.HTTP_202_ACCEPTED)
        
        return Response(result, status=status.HTTP_201_CREATED)
