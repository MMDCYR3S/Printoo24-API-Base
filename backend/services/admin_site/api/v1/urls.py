from django.urls import path, include

urlpatterns = [
    path("users/", include("api.v1.accounts.urls")),
    path("operations/", include("api.v1.operations.urls")),
]

