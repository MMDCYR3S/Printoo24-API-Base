from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderDashboardViewSet

router = DefaultRouter()
router.register('', OrderDashboardViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]

