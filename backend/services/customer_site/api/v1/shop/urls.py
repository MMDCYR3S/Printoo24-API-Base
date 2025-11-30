from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    CategoryViewSet,
    SubmitReviewView,
    ProductFeedbacksView,
    CategoryBannerViewSet
)

app_name = "shop"

urlpatterns = [
    path("grid/", ProductListView.as_view(), name="list"),
    path("detail/<slug:slug>/", ProductDetailView.as_view(), name="detail"),
    path("categories/", CategoryViewSet.as_view({"get": "list"}), name="category-list"),
    path('products/review/<slug:slug>/', SubmitReviewView.as_view(), name='product-review-submit'),
    path('products/feedbacks/<slug:slug>/', ProductFeedbacksView.as_view(), name='product-feedbacks'),
    path('categories/landing/', CategoryBannerViewSet.as_view({'get': 'list'}), name='categories-landing-list'),
    path('categories/landing/<slug:slug>/', CategoryBannerViewSet.as_view({'get': 'retrieve'}), name='categories-landing-detail'),
]
