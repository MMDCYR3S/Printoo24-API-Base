from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    PublicArticleCategoryViewSet,
    PublicArticleViewSet,
    PublicTutorialViewSet
)

router = DefaultRouter()

# ========== PUBLIC ROUTER REGISTRATIONS ========== #
router.register(r'categories', PublicArticleCategoryViewSet, basename='public-blog-category')
router.register(r'articles', PublicArticleViewSet, basename='public-article')
router.register(r'tutorials', PublicTutorialViewSet, basename='public-tutorial')

urlpatterns = [
    path('', include(router.urls)),
]