from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    CalculatePriceView
)

app_name = "shop"

urlpatterns = [
    path("grid/", ProductListView.as_view(), name="list"),
    path("detail/<slug:slug>/", ProductDetailView.as_view(), name="detail"),
    path("calculate-price/", CalculatePriceView.as_view(), name="calculate-price"),
]
