from django.urls import path
from .views import (
    AddToCartView,
    CartItemUpdateView,
    CartItemDetailView,
    CartListView,
    CartItemDeleteView,
    CartClearView,
    CartItemFileUploadView,
    CartItemFileDeleteView
)

app_name = "cart"

urlpatterns = [
    path(
        'add/item/', 
        AddToCartView.as_view(), 
        name='add-item'
    ),
    path(
        'update/item/<int:item_id>/',
        CartItemUpdateView.as_view(),
        name='update-item'
    ),
    path('items/<int:item_id>/upload/', CartItemFileUploadView.as_view(), name='cart-item-upload'),
    path('uploads/<int:upload_id>/', CartItemFileDeleteView.as_view(), name='cart-item-delete-upload'),
    path(
        'items/', 
        CartListView.as_view(), 
        name='cart-items'
    ),
    path(
        'item/<int:item_id>/', 
        CartItemDetailView.as_view(), 
        name='cart-item-detail'
    ),
    path(
        "delete/<int:item_id>/",
        CartItemDeleteView.as_view(),
        name="cart-item-delete"
    ),
    path("clear/", CartClearView.as_view(), name="cart-clear"),
]
