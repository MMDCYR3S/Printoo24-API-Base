from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.core.exceptions import ValidationError

from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductFeedbackStatsSerializer,
    SubmitReviewSerializer,
    CategoryLandingPageSerializer,
    LivePriceCalculationSerializer,
)
from apps.shop.services import (
    ShopProductListService,
    ShopProductDetailService,
    ShopCategoryService,
    FeedbackService,
)
from core.product.services import ProductPricingDomainService
from core.product.exceptions import InvalidProductDataException

# ======= Product List View ======= #
@extend_schema(
    tags=["Product"],
    description="API برای نمایش لیست محصولات همراه با فیلترینگ پیشرفته.",
)
class ProductListView(ListAPIView):
    """
    API View برای نمایش لیست محصولات همراه با فیلترینگ پیشرفته.
    """
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        """
        متد اصلی برای دریافت کوئری‌ست.
        از سرویس لیست محصولات برای گرفتن کوئری‌ست پایه استفاده می‌کند.
        """
        # ====== دریافت سرویس لیست ====== #
        service = ShopProductListService()
        queryset = service.get_base_queryset()
        
        # ===== ایجاد فیلترینگ پیش فرض برای جلوگیری از تکرار داده ها ===== #
        queryset = queryset.prefetch_related(
            'categories',
            'product_image'
        )

        return queryset

# ======= Product Detail View ======= #
@extend_schema(tags=["Product"])
class ProductDetailView(RetrieveAPIView):
    """
    صفحه جزئیات محصول (Single Product Page).
    خروجی شامل تمام آپشن‌ها، قیمت‌ها و قوانین سفارش است.
    """
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        slug = self.kwargs.get(self.lookup_field)
        service = ShopProductDetailService()
        
        try:
            product_instance = service.get_product_detail_for_display(slug=slug)
            
            if product_instance is None:
                return Response({"detail": "محصول یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(product_instance, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": "خطای داخلی سرور.", "error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ======= Category View Set ======= #
@extend_schema(tags=["Category"])
class CategoryViewSet(ViewSet):
    """
    مدیریت نمایش دسته‌بندی‌ها (منو درختی و لندینگ پیج).
    """
    permission_classes = [AllowAny]

    @extend_schema(summary="دریافت درخت دسته‌بندی‌ها (منو)")
    def list(self, request):
        service = ShopCategoryService(request=request)
        tree_data = service.get_category_tree_structure()
        return Response(tree_data)

    @extend_schema(summary="دریافت اطلاعات صفحه لندینگ یک دسته خاص")
    def retrieve(self, request, pk=None): 
        slug = pk 
        service = ShopCategoryService(request=request)
        data = service.get_category_landing_data(slug=slug)
        
        if data is None:
            return Response({"detail": "دسته مورد نظر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = CategoryLandingPageSerializer(data, context={'request': request})
        return Response(serializer.data)
    
@extend_schema(tags=["Category"])
class CategoryBannerViewSet(ViewSet):
    """
    نمایش لیست تمام دسته‌بندی‌های اصلی به همراه:
    1. بنرها (عریض و باکس)
    2. زیر دسته‌ها
    3. محصولات منتخب (خلاصه)
    """
    permission_classes = [AllowAny]

    def list(self, request):
        """
        GET /api/v1/shop/categories-landing/
        """
        service = ShopCategoryService(request=request)
        data_list = service.get_all_categories_with_products()
        serializer = CategoryLandingPageSerializer(data_list, many=True, context={'request': request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, slug=None):
        """
        GET /api/v1/shop/categories-landing/{slug}/
        اگر بخواهید تکی هم بگیرید، این متد استفاده می‌شود (pk اینجا نقش slug را بازی می‌کند اگر lookup_field تنظیم شود)
        """
        service = ShopCategoryService(request=request)
        data = service.get_category_landing_data(slug=slug)
        
        if data is None:
            return Response({"detail": "دسته‌بندی یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = CategoryLandingPageSerializer(data, context={'request': request})
        return Response(serializer.data)



# ===== Submit Review API View ===== #
@extend_schema(tags=["Product-Feedback"])
class SubmitReviewView(APIView):
    """
    ثبت نظر و امتیاز برای یک محصول.
    کاربر باید لاگین باشد و طبق قوانین دامین (خرید محصول) مجاز باشد.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubmitReviewSerializer

    def post(self, request, slug):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = FeedbackService()
        
        try:
            result = service.submit_review(
                user=request.user,
                product_slug=slug,
                data=serializer.validated_data
            )
            
            message = "عملیات با موفقیت انجام شد."
            if 'comment' in result and 'rating' in result:
                message = "امتیاز و نظر شما ثبت شد."
            elif 'comment' in result:
                message = result['comment']
            elif 'rating' in result:
                message = result['rating']

            return Response({"detail": message}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ===== Product Feedback View Set ===== #
@extend_schema(tags=["Product-Feedback"])
class ProductFeedbacksView(APIView):
    """
    نمایش لیست نظرات تایید شده و میانگین امتیاز محصول.
    این API عمومی است (نیاز به لاگین ندارد).
    """
    permission_classes = [AllowAny]
    def get(self, request, slug):
            service = FeedbackService()
            
            try:
                # ===== دریافت سرویس برای دریافت اطلاعات ===== #
                feedbacks_data = service.get_product_feedbacks(product_slug=slug)
                # ===== پاس دادن اطلاعات به 
                serializer = ProductFeedbackStatsSerializer(feedbacks_data)
                return Response(serializer.data, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({"error": "محصول یافت نشد یا خطایی رخ داد."}, status=status.HTTP_404_NOT_FOUND)

# ======= Product Search View ======= #
@extend_schema(
    tags=["Product Search"],
    description="جستجوی محصولات در نام، توضیحات و ویژگی‌های فنی (Options).",
    parameters=[
        OpenApiParameter(
            name='q', 
            type=OpenApiTypes.STR, 
            location=OpenApiParameter.QUERY, 
            description='کلمه کلیدی برای جستجو (مثلاً: گلاسه)',
            required=True
        ),
    ]
)
class ProductSearchView(ListAPIView):
    """
    API اختصاصی برای جستجو با مستندات کامل در Swagger.
    """
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer

    def get_queryset(self):
        # دریافت پارامتر q که در OpenApiParameter تعریف کردیم
        query = self.request.query_params.get('q', '')
        
        # رعایت الگوی Service Layer شما
        service = ShopProductListService()
        
        # لود کردن بهینه داده‌ها (Eager Loading)
        queryset = service.get_search_results(query).prefetch_related(
            'categories',
            'product_image'
        )
        
        return queryset
    
class ProductLivePriceCalculatorView(APIView):
    """
    سرویس محاسبه زنده و لحظه‌ای قیمت محصول.
    """

    @extend_schema(
        tags=["Product"],
        summary="محاسبه لحظه‌ای قیمت (Live Price)",
        description="""
            **راهنمای استفاده برای توسعه‌دهنده فرانت‌اند:**
            لطفاً این API را با استفاده از مکانیزم `Debounce` (مثلاً ۳۰۰ الی ۵۰۰ میلی‌ثانیه) صدا بزنید تا در زمان تایپ کاربر، سرور با ریکوئست‌های رگباری درگیر نشود.
            هربار که کاربر یک Dropdown را تغییر داد یا روی Checkbox کلیک کرد، کل state فعلی فرم را در قالب آبجکت `selections` برای این مسیر POST کنید.
        """,
        request=LivePriceCalculationSerializer,
        
        # ===== مثال‌های بدنه درخواست (Request) ===== #
        examples=[
            OpenApiExample(
                name="نمونه ارسال انتخاب‌های کاربر",
                description="ارسال ترکیبی از دراپ‌داون، چک‌باکس و فیلد متنی",
                value={
                    "selections": {
                        "10": "45",
                        "12": ["50", "51"],
                        "15": "1000",
                        "18": "توضیحات دلخواه"
                    }
                },
                request_only=True,
            )
        ],
        
        # ===== ساختار و مثال‌های رسپانس‌ها (Responses) ===== #
        responses={
            200: OpenApiResponse(
                description="محاسبه موفقیت‌آمیز بود",
                response=inline_serializer(
                    name='LivePriceSuccessResponse',
                    fields={
                        'success': serializers.BooleanField(default=True),
                        'data': inline_serializer(
                            name='LivePriceData',
                            fields={
                                'final_price': serializers.FloatField(),
                                'formatted_price': serializers.CharField(),
                                'summary': inline_serializer(
                                    name='LivePriceSummary',
                                    many=True,
                                    fields={
                                        'field_id': serializers.IntegerField(),
                                        'field_title': serializers.CharField(),
                                        'value': serializers.CharField(),
                                        'choice_id': serializers.IntegerField(allow_null=True, required=False),
                                    }
                                )
                            }
                        )
                    }
                ),
                examples=[
                    OpenApiExample(
                        name="پاسخ موفق",
                        value={
                            "success": True,
                            "data": {
                                "final_price": 25500.0,
                                "formatted_price": "25,500",
                                "summary": [
                                    {
                                        "field_id": 10,
                                        "field_title": "جنس کاغذ",
                                        "value": "گلاسه ۱۳۵ گرم",
                                        "choice_id": 45
                                    }
                                ]
                            }
                        },
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                description="خطای ولیدیشن (مثلاً مقادیر نامعتبر یا اجباری)",
                response=inline_serializer(
                    name='LivePriceErrorResponse',
                    fields={
                        'success': serializers.BooleanField(default=False),
                        'error': serializers.CharField()
                    }
                ),
                examples=[
                    OpenApiExample(
                        name="خطای فیلد اجباری",
                        value={"success": False, "error": "پر کردن فیلد 'تیراژ' الزامی است."},
                        response_only=True
                    )
                ]
            )
        }
    )
    def post(self, request, product_id):
        serializer = LivePriceCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        selections = serializer.validated_data.get('selections', {})
        
        try:
            final_price, configuration_summary = ProductPricingDomainService.calculate_final_price(
                product_id=product_id,
                user_selections=selections,
                strict_validation=False  # <-- برای live price اجباری بودن چک نمیشه
            )
            
            return Response({
                "success": True,
                "data": {
                    "final_price": final_price,
                    "formatted_price": f"{final_price:,.0f}", 
                    "summary": configuration_summary
                }
            }, status=status.HTTP_200_OK)
            
        except InvalidProductDataException as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except ValidationError as e:
            error_msg = str(e.message) if hasattr(e, 'message') else str(e)
            return Response({"success": False, "error": error_msg}, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({"success": False, "error": "خطای سیستمی در محاسبه قیمت رخ داده است."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
