from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiExample

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
    permission_classes = [IsAdminUser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CartDashboardService()

    # ===== مشاهده سبد خرید کاربر ===== #
    @extend_schema(
        summary="مشاهده جزئیات سبد خرید یک کاربر خاص",
        description="ID کاربر را در URL وارد کنید تا سبد خرید فعلی او را ببینید.",
        responses=UserCartDetailSerializer
    )
    def retrieve(self, request, pk=None):
        """ 
        دریافت سبد خرید یک کاربر.
        توجه: pk در اینجا cart_id است.
        """
        data = self.service.get_user_cart_details(cart_id=pk)
        serializer = UserCartDetailSerializer(data['cart'])
        return Response(serializer.data)

    # ===== خالی کردن سبد ===== #
    @extend_schema(summary="حذف کل سبد خرید کاربر")
    def destroy(self, request, pk=None):
        """ pk = cart_id """
        self.service.clear_user_cart(cart_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== افزودن آیتم به سبد کاربر ===== #
    @extend_schema(
        summary="افزودن آیتم به سبد خرید کاربر",
        description="""
        **توضیحات مهم برای فرانت‌اند:**
        
        1. **product_slug**: اسلاگ محصولی که می‌خواهید اضافه کنید.
        2. **selections**: تنظیمات انتخاب شده.
           * `option_value_ids`: لیستی از شناسه (ID) های `ProductOptionValue`. دقت کنید که ID مقدار نهایی انتخاب شده را بفرستید، نه ID گروه ویژگی را.
           * `size_id`: اگر محصول سایز استاندارد دارد (مثل A4)، شناسه سایز را بفرستید.
           * `custom_width` و `custom_height`: اگر محصول متراژی است (مثل بنر)، ابعاد را وارد کنید و `size_id` را نال بگذارید.
        """,
        request=CartItemAddSimpleSerializer,
        responses={201: UserCartDetailSerializer},
        examples=[
            OpenApiExample(
                'Scenario 1: Standard Business Card',
                summary='سناریو ۱: کارت ویزیت (سایز استاندارد + آپشن)',
                description='افزودن کارت ویزیت لمینت. سایز استاندارد انتخاب شده و دو ویژگی (جنس کاغذ و نوع روکش) دارد.',
                value={
                    "product_slug": "envelope-dl-7340",
                    "selections": {
                        "quantity_id": 10,
                        "size_id": 7,
                        "has_design": True,
                        "options": {
                            "9": 22,
                            "10": 25
                        },
                        "custom_width": 0,
                        "custom_height": 0
                    }
                },
                request_only=True,
            ),
            OpenApiExample(
                'Scenario 2: Large Banner',
                summary='سناریو ۲: بنر عریض (ابعاد دلخواه)',
                description='افزودن بنر که مشتری ابعاد خاص (۳ متر در ۱ متر) می‌خواهد.',
                value={
                    "product_slug": "banner-vinyl",
                    "selections": {
                        "quantity": 10,
                        "size_id": None,
                        "custom_width": 300,
                        "custom_height": 100,
                        "has_design": False,
                        "options": {
                            "2": 124,
                            "13": 102
                        },
                    }
                },
                request_only=True,
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
        """ pk = cart_id """
        serializer = CartItemAddSimpleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.service.add_item_to_cart(
                cart_id=pk, 
                data=serializer.validated_data
            )
            
            # ===== مشاهده سبد ===== #
            data = self.service.get_user_cart_details(cart_id=pk)
            return Response(UserCartDetailSerializer(data['cart']).data, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({'detail': e.messages if hasattr(e, 'messages') else str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="ویرایش تعداد یا ویژگی‌های یک آیتم در سبد",
        request=CartItemUpdateSerializer,
        examples=[
            OpenApiExample(
                'Update Quantity',
                summary='فقط تغییر تعداد',
                value={"quantity": 2000}
            ),
            OpenApiExample(
                'Update Quantity Package',
                summary='تغییر بسته تیراژ',
                value={"quantity_id": 51}
            ),
            OpenApiExample(
                'Update Options',
                summary='تغییر آپشن (تغییر روکش)',
                value={
                    "quantity_id": 50,
                    "options": {
                        "10": 101, 
                        "12": 206
                    }
                }
            )
        ]
    )
    @action(detail=True, methods=['patch'], url_path='items/(?P<item_id>\d+)/quantity')
    def update_item(self, request, pk=None, item_id=None):
        """ pk = cart_id, item_id = cart_item.id """
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.service.update_cart_item(
            cart_id=pk, 
            item_id=item_id, 
            data=serializer.validated_data
        )
        return Response({'status': 'Item updated'})

    @extend_schema(summary="حذف آیتم از سبد")
    @action(detail=True, methods=['delete'], url_path='items/(?P<item_id>\d+)')
    def remove_item(self, request, pk=None, item_id=None):
        self.service.remove_item_from_cart(cart_id=pk, item_id=item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # ===== مشاهده لیست تمام سبدها ===== #
    @extend_schema(
        summary="لیست تمام سبدهای خرید فعال",
        description="لیست کاربرانی که در سبد خریدشان محصولی دارند (جهت پیگیری فروش).",
        responses=CartListSerializer(many=True)
    )
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
