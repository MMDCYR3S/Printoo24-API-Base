from rest_framework import viewsets, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db.models import F

from apps.blog.models import ArticleCategory, Article, Tutorial, ArticleStatus

from .serializers import (
    PublicArticleCategorySerializer,
    PublicArticleListSerializer,
    PublicArticleDetailSerializer,
    PublicTutorialListSerializer,
    PublicTutorialDetailSerializer
)

# ========== PUBLIC BLOG CATEGORY VIEW ========== #
@extend_schema(tags=['Blog-Tutorial'])
class PublicArticleCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    دریافت لیست دسته‌بندی‌های فعال بلاگ
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = PublicArticleCategorySerializer
    
    def get_queryset(self):
        return ArticleCategory.objects.filter(is_active=True).order_by('id')


# ========== PUBLIC ARTICLE VIEW ========== #
@extend_schema(tags=['Blog-Tutorial'])
class PublicArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    دریافت لیست مقالات منتشر شده و جزئیات آن‌ها
    """
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # فقط مقالاتی که منتشر شده‌اند و دسته‌بندی آن‌ها نیز فعال است
        return Article.objects.select_related('author', 'category').prefetch_related('related_products').filter(
            status=ArticleStatus.PUBLISHED,
            category__is_active=True
        ).order_by('-published_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PublicArticleDetailSerializer
        return PublicArticleListSerializer

    def retrieve(self, request, *args, **kwargs):
        # 🌟 یک ایده سینیوری: وقتی کاربر وارد صفحه جزئیات مقاله می‌شود، یک بازدید به شمارنده اضافه کنیم
        instance = self.get_object()
        
        # آپدیت بهینه فقط برای فیلد views_count بدون درگیر کردن سیگنال‌ها و بقیه فیلدها
        Article.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        instance.views_count += 1 
        
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)


# ========== PUBLIC TUTORIAL VIEW ========== #
@extend_schema(tags=['Blog-Tutorial'])
class PublicTutorialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    دریافت لیست آموزش‌های ویدیویی فعال و جزئیات آن‌ها
    """
    permission_classes = [permissions.AllowAny] 

    def get_queryset(self):
        # فقط آموزش‌های فعال
        return Tutorial.objects.prefetch_related('related_products').filter(
            is_active=True
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PublicTutorialDetailSerializer
        return PublicTutorialListSerializer