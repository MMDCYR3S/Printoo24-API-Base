from django.urls import path, include

app_name = "v1"

urlpatterns = [
    path("authentication/", include("api.v1.authentication.urls")),
]
