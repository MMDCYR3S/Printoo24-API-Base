from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.shop.filters import ProductFilter
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductFeedbackStatsSerializer,
    SubmitReviewSerializer,
    CategoryLandingPageSerializer,
)
from apps.shop.services import (
    ShopProductListService,
    ShopProductDetailService,
    ShopCategoryService,
    FeedbackService,
)

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
    filterset_class = ProductFilter
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
        filterset = self.filterset_class(self.request.GET, queryset=queryset)

        return filterset.qs.distinct()

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