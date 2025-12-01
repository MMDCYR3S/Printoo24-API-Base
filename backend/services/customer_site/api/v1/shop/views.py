from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from drf_spectacular.utils import extend_schema

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
from core.models import Product

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
    
    def get_queryset(self):
        """
        متد اصلی برای دریافت کوئری‌ست.
        از سرویس لیست محصولات برای گرفتن کوئری‌ست پایه استفاده می‌کند.
        """
        # ====== دریافت سرویس لیست ====== #
        service = ShopProductListService()
        queryset = service.get_base_queryset()
        
        # ===== ایجاد فیلترینگ پیش فرض برای جلوگیری از تکرار داده ها ===== #
        filterset = self.filterset_class(self.request.GET, queryset=queryset)
        
        return filterset.qs.distinct()


# ====== Product Detail View ====== #
@extend_schema(
    tags=["Product"],
    description="API برای نمایش لیست محصولات همراه با فیلترینگ پیشرفته.",
)
class ProductDetailView(RetrieveAPIView):
    """
    API View برای نمایش جزئیات کامل یک محصول با تمام گزینه‌های قیمت‌گذاری.
    """
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
    queryset = Product.objects.filter(is_active=True)

    def retrieve(self, request, *args, **kwargs):
        """
        این متد را override می‌کنیم تا از سرویس خودمان برای آماده‌سازی داده‌ها استفاده کنیم.
        """
        slug = self.kwargs.get(self.lookup_field)
        
        # ===== ایجاد سرویس برای دریافت اطلاعات پایه ===== #
        service = ShopProductDetailService()
        product_data_dict = service.get_product_detail_for_display(slug=slug)

        # ===== بررسی وجود محصول ===== #
        if product_data_dict is None:
            return Response({"detail": "محصول مورد نظر پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)

        # ===== ساخت سریالایزر به واسطه داده های بازگشتی از سرویس ===== #
        serializer = self.get_serializer(product_data_dict)
        
        # ===== دریافت پاسخ نهایی ===== #
        return Response(serializer.data)

# ======= Category View Set ======= #
@extend_schema(tags=["Product"])
class CategoryViewSet(ViewSet):
    """
    ViewSet برای مدیریت دسته‌بندی‌ها و درختواره دسته‌بندی‌ها.
    """
    permission_classes = [AllowAny]

    def list(self, request):
        service = ShopCategoryService(request=request)
        
        tree_data = service.get_category_tree_structure()
        return Response(tree_data)
    
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
        
        # فراخوانی متد جدید که لیست برمی‌گرداند
        data_list = service.get_all_categories_with_products()
        
        # نکته مهم: چون خروجی یک لیست است، many=True را اضافه می‌کنیم
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
