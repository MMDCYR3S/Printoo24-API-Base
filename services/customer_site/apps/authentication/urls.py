from django.urls import path, include
from .views import RegisterAPIView

app_name = "authentication"

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register")
]

