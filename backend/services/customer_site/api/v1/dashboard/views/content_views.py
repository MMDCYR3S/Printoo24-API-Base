from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.dashboard.services.content_service import (
    DashboardArticleCategoryService, 
    DashboardBlogService, 
    DashboardTutorialService
)
from ..serializers import (
    ArticleCategoryReadSerializer, ArticleCategoryWriteSerializer,
    ArticleReadSerializer, ArticleWriteSerializer,
    TutorialReadSerializer, TutorialWriteSerializer,
    BulkActionSerializer, BulkStatusSerializer
)

# ========== BLOG CATEGORY VIEW ========== #
@extend_schema(tags=['Dashboard-Blog-Category'])
class ArticleCategoryViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_service = DashboardArticleCategoryService()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ArticleCategoryReadSerializer
        return ArticleCategoryWriteSerializer

    @extend_schema(summary="لیست تمام دسته‌بندی‌های بلاگ")
    def list(self, request):
        categories = self.app_service.get_all_categories()
        serializer = self.get_serializer_class()(categories, many=True)
        return Response(serializer.data)

    @extend_schema(summary="ایجاد دسته‌بندی جدید")
    def create(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = self.app_service.create_category(serializer.validated_data)
        # خروجی با سریالایزر Read برگردانده می‌شود
        return Response(ArticleCategoryReadSerializer(category).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="دریافت جزئیات یک دسته")
    def retrieve(self, request, pk=None):
        category = self.app_service.get_category_detail(pk)
        return Response(self.get_serializer_class()(category).data)

    @extend_schema(summary="ویرایش دسته‌بندی")
    def update(self, request, pk=None):
        serializer = self.get_serializer_class()(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        category = self.app_service.update_category(pk, serializer.validated_data)
        return Response(ArticleCategoryReadSerializer(category).data)

    @extend_schema(summary="حذف تکی دسته‌بندی")
    def destroy(self, request, pk=None):
        self.app_service.delete_category(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(summary="ویرایش وضعیت گروهی دسته‌بندی‌ها", request=BulkStatusSerializer)
    @action(detail=False, methods=['patch'], url_path='bulk-status')
    def bulk_status(self, request):
        serializer = BulkStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_count = self.app_service.bulk_update_status(
            serializer.validated_data['ids'], 
            serializer.validated_data['is_active']
        )
        return Response({'message': f'{updated_count} دسته‌بندی ویرایش شد.'})

    @extend_schema(summary="حذف گروهی دسته‌بندی‌ها", request=BulkActionSerializer)
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        serializer = BulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        deleted_count = self.app_service.bulk_delete(serializer.validated_data['ids'])
        return Response({'message': f'{deleted_count} دسته‌بندی با موفقیت حذف شد.'})


# ========== ARTICLE VIEW ========== #
@extend_schema(tags=['Dashboard-Article'])
class ArticleViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_service = DashboardBlogService()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ArticleReadSerializer
        return ArticleWriteSerializer

    @extend_schema(summary="لیست تمام مقالات")
    def list(self, request):
        articles = self.app_service.get_all_articles()
        serializer = self.get_serializer_class()(articles, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        summary="ایجاد مقاله جدید",
        description="""
        **وضعیت‌های مجاز برای مقاله (Article Status):**
        - `draft` : پیش‌نویس
        - `published` : منتشر شده
        - `archived` : بایگانی شده
        """
    )
    def create(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        article = self.app_service.create_article(request.user, serializer.validated_data)
        return Response(ArticleReadSerializer(article).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="دریافت جزئیات مقاله")
    def retrieve(self, request, pk=None):
        article = self.app_service.get_article_detail(pk)
        return Response(self.get_serializer_class()(article).data, context={'request': request})

    @extend_schema(
        summary="ویرایش مقاله",
        description="""
        **وضعیت‌های مجاز برای مقاله (Article Status):**
        - `draft` : پیش‌نویس
        - `published` : منتشر شده
        - `archived` : بایگانی شده
        """
    )
    def update(self, request, pk=None):
        serializer = self.get_serializer_class()(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        article = self.app_service.update_article(pk, serializer.validated_data)
        return Response(ArticleReadSerializer(article).data)

    @extend_schema(summary="حذف تکی مقاله")
    def destroy(self, request, pk=None):
        self.app_service.delete_article(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="تغییر وضعیت گروهی مقالات", 
        description="""
        **وضعیت‌های مجاز برای status:**
        - `draft` : پیش‌نویس
        - `published` : منتشر شده
        - `archived` : بایگانی شده
        """,
        request=BulkStatusSerializer
    )
    @action(detail=False, methods=['patch'], url_path='bulk-status')
    def bulk_status(self, request):
        serializer = BulkStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_count = self.app_service.bulk_update_status(
            serializer.validated_data['ids'], 
            serializer.validated_data['status']
        )
        return Response({'message': f'{updated_count} مقاله ویرایش شد.'})

    @extend_schema(summary="حذف گروهی مقالات", request=BulkActionSerializer)
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        serializer = BulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        deleted_count = self.app_service.bulk_delete(serializer.validated_data['ids'])
        return Response({'message': f'{deleted_count} مقاله با موفقیت حذف شد.'})


# ========== TUTORIAL VIEW ========== #
@extend_schema(tags=['Dashboard-Tutorial'])
class TutorialViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_service = DashboardTutorialService()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TutorialReadSerializer
        return TutorialWriteSerializer

    @extend_schema(summary="لیست تمام آموزش‌ها")
    def list(self, request):
        tutorials = self.app_service.get_all_tutorials()
        serializer = self.get_serializer_class()(tutorials, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(summary="ایجاد آموزش جدید")
    def create(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        tutorial = self.app_service.create_tutorial(serializer.validated_data)
        return Response(TutorialReadSerializer(tutorial).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="دریافت جزئیات آموزش")
    def retrieve(self, request, pk=None):
        tutorial = self.app_service.get_tutorial_detail(pk)
        return Response(self.get_serializer_class()(tutorial).data, context={'request': request})

    @extend_schema(summary="ویرایش آموزش")
    def update(self, request, pk=None):
        serializer = self.get_serializer_class()(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        tutorial = self.app_service.update_tutorial(pk, serializer.validated_data)
        return Response(TutorialReadSerializer(tutorial).data)

    @extend_schema(summary="حذف تکی آموزش")
    def destroy(self, request, pk=None):
        self.app_service.delete_tutorial(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(summary="تغییر وضعیت گروهی آموزش‌ها", request=BulkStatusSerializer)
    @action(detail=False, methods=['patch'], url_path='bulk-status')
    def bulk_status(self, request):
        serializer = BulkStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_count = self.app_service.bulk_update_status(
            serializer.validated_data['ids'], 
            serializer.validated_data['is_active']
        )
        return Response({'message': f'{updated_count} آموزش ویرایش شد.'})

    @extend_schema(summary="حذف گروهی آموزش‌ها", request=BulkActionSerializer)
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        serializer = BulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        deleted_count = self.app_service.bulk_delete(serializer.validated_data['ids'])
        return Response({'message': f'{deleted_count} آموزش با موفقیت حذف شد.'})
