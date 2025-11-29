from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    CategoryViewSet
)

app_name = "shop"

urlpatterns = [
    path("grid/", ProductListView.as_view(), name="list"),
    path("detail/<slug:slug>/", ProductDetailView.as_view(), name="detail"),
    path("categories/", CategoryViewSet.as_view({"get": "list"}), name="category-list"),
]
