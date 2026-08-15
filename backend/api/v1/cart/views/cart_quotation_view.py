from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from apps.cart.services import CartQuotationService
from ..serializers import CartQuotationListSerializer, CartQuotationDetailSerializer

@extend_schema(tags=['Cart'])
class CartQuotationListView(GenericAPIView):
    """
    نمایش لیست پیش‌فاکتورهای سبد خرید.
    """
    permission_classes = [AllowAny]
    serializer_class = CartQuotationListSerializer

    @extend_schema(
        summary="لیست پیش‌فاکتورهای سبد خرید",
        description="تمام پیش‌فاکتورهایی که برای آیتم‌های سبد خرید ساخته شده‌اند را برمی‌گرداند.",
        parameters=[
            OpenApiParameter(
                name='X-Guest-Token',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.HEADER,
                description='شناسه یکتا برای کاربر مهمان (اگر لاگین نیست)',
                required=False
            )
        ],
        responses={200: CartQuotationListSerializer(many=True)}
    )
    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        service = CartQuotationService()
        quotations = service.get_cart_quotations(user=user, session_key=session_key)

        serializer = self.get_serializer(quotations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@extend_schema(tags=['Cart'])
class CartItemQuotationDetailView(GenericAPIView):
    """
    نمایش جزئیات پیش‌فاکتور مرتبط با یک آیتم سبد خرید.
    """
    permission_classes = [AllowAny]
    serializer_class = CartQuotationDetailSerializer

    @extend_schema(
        summary="جزئیات پیش‌فاکتور بر اساس آیتم سبد خرید",
        description="با ارسال شناسه آیتم سبد خرید، پیش‌فاکتور مرتبط با آن برگردانده می‌شود.",
        parameters=[
            OpenApiParameter(
                name='X-Guest-Token',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.HEADER,
                description='شناسه یکتا برای کاربر مهمان (اگر لاگین نیست)',
                required=False
            )
        ],
        responses={200: CartQuotationDetailSerializer}
    )
    def get(self, request, item_id):
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        service = CartQuotationService()
        quotation = service.get_quotation_by_cart_item(
            cart_item_id=item_id,
            user=user,
            session_key=session_key,
        )

        serializer = self.get_serializer(quotation)
        return Response(serializer.data, status=status.HTTP_200_OK)