from django.urls import path
from .views import (
    TemporaryFileUploadView,
    AddToCartView,
    CartItemUpdateView,
    CartItemDetailView,
    CartListView,
)

app_name = "cart"

urlpatterns = [
    path(
        'upload-temporary-file/', 
        TemporaryFileUploadView.as_view(), 
        name='upload-temporary-file'
    ),
    path(
        'add/item/', 
        AddToCartView.as_view(), 
        name='add-item'
    ),
    path(
        'update/item/<int:item_id>/',
        CartItemUpdateView.as_view(),
        name='cart-item-update-config'
    ),
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
]
