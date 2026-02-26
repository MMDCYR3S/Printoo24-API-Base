from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.dashboard.services import CartDashboardService, CartFileService
from ..serializers import (
    UserCartDetailSerializer,
    CartItemAddSimpleSerializer,
    CartItemUpdateSerializer,
    CartListSerializer,
    CartFileUploadSerializer,
)


# ===== Cart Dashboard ViewSet ===== #
@extend_schema(tags=['Dashboard-Cart'])
class CartDashboardViewSet(viewsets.ViewSet):
    """
    مدیریت سبد خرید کاربران توسط ادمین.
    pk در همه اکشن‌ها = cart_id
    """
    permission_classes = [IsAdminUser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CartDashboardService()

    # ===== LIST ===== #
    @extend_schema(
        summary="لیست تمام سبدهای خرید فعال",
        description="لیست کاربرانی که در سبد خریدشان محصولی دارند (جهت پیگیری فروش).",
        responses=CartListSerializer(many=True)
    )
    def list(self, request):
        queryset = self.service.get_all_carts_queryset()
        serializer = CartListSerializer(queryset, many=True)
        return Response(serializer.data)

    # ===== RETRIEVE ===== #
    @extend_schema(
        summary="مشاهده جزئیات سبد خرید یک کاربر خاص",
        responses=UserCartDetailSerializer
    )
    def retrieve(self, request, pk=None):
        data = self.service.get_user_cart_details(cart_id=pk)
        serializer = UserCartDetailSerializer(data['cart'])
        return Response(serializer.data)

    # ===== DESTROY (clear cart) ===== #
    @extend_schema(summary="حذف کل سبد خرید کاربر")
    def destroy(self, request, pk=None):
        # ===== اصلاح نام متد: clear_user_cart (نه clear_cart) ===== #
        self.service.clear_user_cart(cart_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== ADD ITEM ===== #
    @extend_schema(
        summary="افزودن آیتم به سبد خرید کاربر",
        description="""
**توضیحات مهم:**

- `product_slug`: اسلاگ محصول (اختیاری — اگر خالی باشد، آیتم دستی ثبت می‌شود)
- `selections`: شامل `field_<id>` برای هر `ProductField`، `quantity` و سایر تنظیمات
- برای آیتم دستی (بدون محصول): `name` و `price` اجباری‌اند
        """,
        request=CartItemAddSimpleSerializer,
        responses={201: UserCartDetailSerializer},
        examples=[
            OpenApiExample(
                'Scenario 1: Product with Field Selections',
                summary='محصول با انتخاب فیلدها (ProductField)',
                value={
                    "product_slug": "catalog-print",
                    "selections": {
                        "field_12": 3,
                        "field_15": 500,
                        "quantity": 100,
                        "has_design": True
                    }
                },
                request_only=True,
            ),
            OpenApiExample(
                'Scenario 2: Manual Item (No Product)',
                summary='آیتم دستی بدون محصول',
                value={
                    "product_slug": None,
                    "name": "هزینه طراحی لوگو",
                    "price": 850000,
                    "selections": {"quantity": 1}
                },
                request_only=True,
            ),
        ]
    )
    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
        serializer = CartItemAddSimpleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.service.add_item_to_cart(cart_id=pk, data=serializer.validated_data)
            data = self.service.get_user_cart_details(cart_id=pk)
            return Response(UserCartDetailSerializer(data['cart']).data, status=status.HTTP_201_CREATED)

        except (ValidationError, DRFValidationError) as e:
            detail = e.messages if hasattr(e, 'messages') else str(e)
            return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== UPDATE ITEM ===== #
    @extend_schema(
        summary="ویرایش تعداد یا ویژگی‌های یک آیتم در سبد",
        request=CartItemUpdateSerializer,
        examples=[
            OpenApiExample(
                'Update with field selections',
                value={
                    "field_12": 3,
                    "field_15": 200,
                    "quantity": 50,
                    "has_design": True
                }
            ),
        ]
    )
    @action(detail=True, methods=['patch'], url_path='items/(?P<item_id>\d+)/quantity')
    def update_item(self, request, pk=None, item_id=None):
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.service.update_cart_item(
                cart_id=pk,
                item_id=item_id,
                data=serializer.validated_data
            )
            return Response({'status': 'Item updated'})
        except (ValidationError, DRFValidationError) as e:
            detail = e.messages if hasattr(e, 'messages') else str(e)
            return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== REMOVE ITEM ===== #
    @extend_schema(summary="حذف آیتم از سبد")
    @action(detail=True, methods=['delete'], url_path='items/(?P<item_id>\d+)')
    def remove_item(self, request, pk=None, item_id=None):
        try:
            self.service.remove_item_from_cart(cart_id=pk, item_id=item_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ===== Cart File Upload ViewSet ===== #
@extend_schema(tags=['Dashboard-Cart'])
class CartFileUploadViewSet(viewsets.ViewSet):
    """
    مدیریت آپلود فایل‌های طراحی توسط کاربر.
    pk = CartItem ID
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CartFileService()

    @extend_schema(
        summary="آپلود فایل طراحی برای آیتم سبد خرید",
        request=CartFileUploadSerializer
    )
    @action(detail=True, methods=['post'], url_path='upload')
    def upload_for_item(self, request, pk=None):
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

        status_code = status.HTTP_202_ACCEPTED if result.get('status') == 'processing' else status.HTTP_201_CREATED
        return Response(result, status=status_code)
