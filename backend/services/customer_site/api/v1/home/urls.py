from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SliderViewSet, ContactUsView, PromotionalModalView

router = DefaultRouter()
router.register(r'sliders', SliderViewSet, basename='sliders')

urlpatterns = [
    path('', include(router.urls)),
    path('contact/', ContactUsView.as_view(), name='contact'),
    path('modals/', PromotionalModalView.as_view(), name='modals'),
]
