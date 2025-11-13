from django.urls import path, include
from .views import RegisterAPIView, VerifyEmailApiView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path("verify/", VerifyEmailApiView.as_view(), name="verify-email"),
]
