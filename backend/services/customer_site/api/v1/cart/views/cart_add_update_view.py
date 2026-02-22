from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiTypes

from ..serializers import AddToCartSerializer, CartItemUpdateSerializer
from apps.cart.services import AddToCartService, CartItemUpdateService # فرض بر این است که سرویس آپدیت را هم مشابه Add نوشته‌اید
from core.infrastructure.messages import msg_provider

def get_session_key(request):
    """
    اگر کاربر سشن ندارد، برایش می‌سازیم و کلیدش را برمی‌گردانیم.
    """
    if not request.session.exists(request.session.session_key):
        request.session.create()
    return request.session.session_key

# ===== Add To Cart View ===== #
@extend_schema(tags=["Cart"])
class AddToCartView(GenericAPIView):
    """
    POST /api/v1/cart/add/
    """
    permission_classes = [AllowAny]
    serializer_class = AddToCartSerializer
    
    @extend_schema(
        summary="افزودن محصول داینامیک به سبد خرید",
        description="""
        **معماری جدید (Dynamic Form Builder):**
        لطفاً متغیرهای هاردکد مثل `size_id` یا `quantity` را فراموش کنید!
        کافیست فرمی که از API جزئیات محصول گرفته‌اید را رندر کنید و هرچه کاربر انتخاب کرد را به صورت کلید-مقدار در آبجکت `selections` بفرستید.
        سیستم هوشمند بک‌اند، بر اساس فرمول‌های ادمین، قیمت کل را محاسبه করে و به سبد اضافه می‌کند.
        
        **نکات مهم:**
        1. کلیدهای دیکشنری `selections` همان `id` فیلدهایی است که از سرور گرفته‌اید.
        2. اگر فیلدی چندانتخابی (Multi Select) است، مقدار آن را به صورت لیست (Array) بفرستید.
        3. می‌توانید مقادیر متنی `name` و `description` را مستقیماً داخل `selections` بفرستید تا روی سفارش ذخیره شوند.
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
        responses={201: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                '1. Standard Print (Business Card)',
                summary='سناریو ۱: چاپ استاندارد (کارت ویزیت با آپشن و تیراژ)',
                description='فرض کنید فیلد ۱۰ (جنس کاغذ) و فیلد ۱۲ (تیراژ) و فیلد ۱۵ (خدمات-چندانتخابی) است.',
                value={
                    "product_id": 105,
                    "selections": {
                        "name": "کارت ویزیت شخصی علی",      # فیلد ثابت برای نام‌گذاری سفارش
                        "description": "گوشه‌ها دقیق گرد شود", # فیلد ثابت برای یادداشت
                        "10": 45,                           # کاربر گزینه "گلاسه مات" (id:45) را انتخاب کرده
                        "12": 25,                         # کاربر تیراژ ۱۰۰۰ را وارد کرده
                        "15": [88, 92]                      # کاربر دو چک‌باکس طلاکوب(88) و دورگرد(92) را تیک زده
                    }
                },
                request_only=True
            ),
            OpenApiExample(
                '2. Banner (Dimensional Product)',
                summary='سناریو ۲: محصول متراژی (بنر)',
                description='فرض کنید فیلد ۲۰ (طول)، فیلد ۲۱ (عرض) و فیلد ۲۲ (نوع پانچ) است.',
                value={
                    "product_id": 300,
                    "selections": {
                        "name": "بنر سر در مغازه",
                        "20": 3,                          # کاربر طول را 3.5 متر وارد کرده
                        "21": 5,                          # کاربر عرض را 1.2 متر وارد کرده
                        "22": 12                          # انتخاب گزینه "پانچ ۴ گوشه" (id:110)
                    }
                },
                request_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # ===== استخراج شناسه کاربر و مهمان ===== #
        user = request.user if request.user.is_authenticated else None
        session_key = None
        if not user:
            session_key = get_session_key(request)

        try:
            # ===== اجرای سرویس ===== #
            service = AddToCartService(user=user, session_key=session_key)
            cart_item = service.execute(
                product_id=data["product_id"],
                selections=data["selections"]
            )
            return Response(
                {"id": cart_item.id, "message": msg_provider.get("cart.S4001", default="محصول با موفقیت به سبد اضافه شد.")}, 
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ===== Cart Item Update View ===== #
@extend_schema(tags=["Cart"])
class CartItemUpdateView(GenericAPIView):
    """
    PATCH /api/v1/cart/items/{item_id}/
    """
    permission_classes = [AllowAny]
    serializer_class = CartItemUpdateSerializer

    @extend_schema(
        summary="ویرایش کانفیگ و ویژگی‌های یک آیتم در سبد خرید",
        description="""
        اگر مشتری خواست ویژگی محصولی که در سبد خرید است را تغییر دهد (مثلاً تیراژ را از ۱۰۰۰ به ۲۰۰۰ تغییر دهد)، 
        کل دیکشنری `selections` جدید را به این اندپوینت بفرستید. 
        بک‌اند قیمت را مجدداً با فرمول محاسبه کرده و سبد را آپدیت می‌کند.
        """,
        parameters=[
            OpenApiParameter("item_id", OpenApiTypes.INT, OpenApiParameter.PATH, description="شناسه ردیف سبد خرید (CartItem ID)"),
            OpenApiParameter(
                name='X-Guest-Token',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.HEADER,
                description='شناسه یکتا برای کاربر مهمان',
                required=False
            )
        ],
        examples=[
            OpenApiExample(
                'Update Config',
                summary='تغییر تیراژ و یادداشت',
                value={
                    "selections": {
                        "name": "کارت ویزیت شخصی علی",
                        "description": "گوشه‌ها دقیق گرد شود (اصلاحیه: تیراژ بالا رفت)", 
                        "10": 45,       
                        "12": 2000,     # <--- این عدد توسط کاربر تغییر کرده است
                        "15": [88, 92]
                    }
                }
            )
        ]
    )
    def patch(self, request, item_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user if request.user.is_authenticated else None
        
        # ===== استخراج شناسه کاربر و مهمان ===== #
        session_key = None
        if not user:
            session_key = get_session_key(request)

        try:
            # ===== اجرای سرویس (فرض بر اینکه CartItemUpdateService از منطق CartProcessor استفاده می‌کند) ===== #
            service = CartItemUpdateService(user=user, session_key=session_key)
            updated_item = service.update(
                cart_item_id=item_id,
                selections=serializer.validated_data['selections']
            )
            return Response(
                {"id": updated_item.id, "message": msg_provider.get("cart.S4005", default="سبد خرید بروزرسانی شد.")}, 
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
