from django.urls import path
from .views import (
    TemporaryFileUploadView,
    AddToCartView
)

app_name = "cart"

urlpatterns = [
    path(
        'upload-temporary-file/', 
        TemporaryFileUploadView.as_view(), 
        name='upload-temporary-file'
    ),
    path(
        'add-item/', 
        AddToCartView.as_view(), 
        name='add-item'
    ),
]
