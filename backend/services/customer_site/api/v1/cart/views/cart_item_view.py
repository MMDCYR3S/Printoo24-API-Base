from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from apps.cart.services import CartListService, CartItemDetailService
from ..serializers import CartListSerializer, CartItemDetailSerializer

# ======== Cart List View ======== #
@extend_schema(tags=['Cart'])
class CartListView(GenericAPIView):
    """
    نمایش لیست سبد خرید.
    """
    permission_classes = [AllowAny]
    serializer_class = CartListSerializer

    @extend_schema(
        summary="مشاهده سبد خرید و آیتم‌ها",
        description="""
        لیست تمام آیتم‌های موجود در سبد خرید کاربر را برمی‌گرداند.
        دقت کنید که فیلد `configuration` داخل هر آیتم، نشان‌دهنده ویژگی‌های انتخابی کاربر (مثل سایز، روکش، تیراژ) است.
        """,
        parameters=[
            OpenApiParameter(
                name='X-Guest-Token',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.HEADER,
                description='شناسه یکتا برای کاربر مهمان (اگر لاگین نیست)',
                required=False
            )
        ],
        responses={200: CartListSerializer}
    )
    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        
        # مدیریت سشن مهمان
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        service = CartListService()
        data = service.get_cart_details(user=user, session_key=session_key)
        
        cart = data['cart']
        
        if not cart:
            return Response({
                "id": None,
                "items": [],
                "total_price": 0,
                "total_items": 0,
                "updated_at": None
            }, status=status.HTTP_200_OK)
            
        serializer = self.get_serializer(cart, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

# ======== Cart Item Detail View ======== #
@extend_schema(tags=['Cart'])
class CartItemDetailView(GenericAPIView):
    """
    نمایش جزئیات یک آیتم خاص در سبد خرید.
    """
    permission_classes = [AllowAny]
    serializer_class = CartItemDetailSerializer
    
    @extend_schema(
        summary="دریافت جزئیات یک آیتم از سبد خرید",
        parameters=[
            OpenApiParameter("item_id", OpenApiTypes.INT, OpenApiParameter.PATH, description="شناسه آیتم"),
            OpenApiParameter(
                name='X-Guest-Token',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.HEADER,
                description='شناسه یکتا برای کاربر مهمان',
                required=False
            )
        ]
    )
    def get(self, request, item_id):
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key
        
        service = CartItemDetailService()
        
        try:
            item = service.get_item_detail(
                item_id=item_id, 
                user=user, 
                session_key=session_key
            )
            serializer = self.get_serializer(item, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ObjectDoesNotExist:
            return Response(
                {"detail": msg_provider.get("cart.E4002", default="آیتم یافت نشد.")}, 
                status=status.HTTP_404_NOT_FOUND
            )
