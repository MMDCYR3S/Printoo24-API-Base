from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes

from core.home.services import SliderService
from core.models import PromotionalModal, SliderIndex
from .serializers import SliderSerializer, PromotionalModalSerializer, ContactUsSerializer

# ===== Slider ViewSet (Customer Side) ===== #
@extend_schema(tags=['General - Content'])
class SliderViewSet(viewsets.ViewSet):
    """
    نمایش اسلایدرهای صفحه اصلی برای مشتریان.
    این ویو فقط قابلیت خواندن (Read-Only) دارد.
    """
    permission_classes = [AllowAny] # همه کاربران (حتی مهمان) باید ببینند

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SliderService()

    @extend_schema(
        summary="دریافت لیست اسلایدرها",
        description="لیست تصاویر برای نمایش در اسلایدر بالای صفحه اصلی.",
        responses={200: SliderSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Slider List Example',
                value=[
                    {
                        "id": 1,
                        "name": "تخفیف بهاره",
                        "image_url": "https://api.printoo.ir/media/slider/spring_sale.jpg"
                    },
                    {
                        "id": 2,
                        "name": "محصولات جدید",
                        "image_url": "https://api.printoo.ir/media/slider/new_arrival.jpg"
                    }
                ]
            )
        ]
    )
    def list(self, request):
        queryset = self.service.get_all()
        serializer = SliderSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# ===== 2. PROMOTIONAL MODAL VIEW ===== #
@extend_schema(tags=['General - Content'])
class PromotionalModalView(APIView):
    """
    دریافت مودال تبلیغاتی فعال.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="دریافت مودال فعال",
        description="""
        این متد **تنها یک آبجکت** برمی‌گرداند (آخرین مودالی که `is_active=True` باشد).
        اگر هیچ مودال فعالی نباشد، پاسخ `200 OK` با مقدار `null` یا دیکشنری خالی برمی‌گردد.
        فرانت باید چک کند که آیا دیتایی دریافت کرده یا خیر.
        """,
        responses={200: PromotionalModalSerializer},
        examples=[
            OpenApiExample(
                'Active Modal Found',
                summary='مودال فعال',
                value={
                    "id": 5,
                    "title": "جشنواره یلدا",
                    "description": "با کد YALDA از ۲۰ درصد تخفیف بهره‌مند شوید.",
                    "image_url": "https://api.printoo.ir/media/banners/modal_yalda.jpg",
                    "cta_text": "مشاهده تخفیف‌ها",
                    "cta_url": "https://printoo.ir/products/category/yalda"
                }
            ),
            OpenApiExample(
                'No Active Modal',
                summary='بدون مودال',
                value=None  # یا {}
            )
        ]
    )
    def get(self, request):
        # دریافت آخرین مودال فعال
        modal = PromotionalModal.objects.filter(is_active=True).last()
        
        if modal:
            serializer = PromotionalModalSerializer(modal, context={'request': request})
            return Response(serializer.data)
        
        # اگر مودالی نبود، None برمی‌گردانیم (فرانت باید هندل کند)
        return Response(None, status=status.HTTP_200_OK)


# ===== 3. CONTACT US VIEW ===== #
@extend_schema(tags=['General - Contact'])
class ContactUsView(APIView):
    """
    فرم تماس با ما.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="ارسال پیام تماس با ما",
        request=ContactUsSerializer,
        responses={201: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Contact Form Submit',
                value={
                    "full_name": "علی محمدی",
                    "email": "ali@example.com",
                    "phone_number": "09123456789",
                    "subject": "همکاری در فروش",
                    "message": "با سلام، درخواست همکاری دارم..."
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "پیام شما با موفقیت دریافت شد. کارشناسان ما به زودی با شما تماس می‌گیرند."}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    