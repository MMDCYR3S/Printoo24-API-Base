from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    CategoryViewSet,
    SubmitReviewView,
    ProductFeedbacksView,
    CategoryBannerViewSet,
    ProductSearchView,
    ProductLivePriceCalculatorView
)

app_name = "shop"

urlpatterns = [
    path("grid/", ProductListView.as_view(), name="list"),
    path("detail/<str:slug>/", ProductDetailView.as_view(), name="detail"),
    path("categories/", CategoryViewSet.as_view({"get": "list"}), name="category-list"),
    path('products/review/<str:slug>/', SubmitReviewView.as_view(), name='product-review-submit'),
    path('products/feedbacks/<str:slug>/', ProductFeedbacksView.as_view(), name='product-feedbacks'),
    path('categories/landing/', CategoryBannerViewSet.as_view({'get': 'list'}), name='categories-landing-list'),
    path('categories/landing/<str:slug>/', CategoryBannerViewSet.as_view({'get': 'retrieve'}), name='categories-landing-detail'),
    path("search/", ProductSearchView.as_view(), name="product-search"),
    path(
        'products/<int:product_id>/calculate-price/', 
        ProductLivePriceCalculatorView.as_view(), 
        name='live-price-calculator'
    ),
]
