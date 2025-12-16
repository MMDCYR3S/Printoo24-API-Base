from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ShipmentViewSet,
    LogisticCostViewSet,
    DeliveryMethodViewSet
)

router = DefaultRouter()
router.register(r'delivery/method', DeliveryMethodViewSet, basename='delivery')
router.register(r'shipments', ShipmentViewSet, basename='shipment')
# router.register(r'costs', LogisticCostViewSet, basename='logistic-cost')

urlpatterns = [
    path('', include(router.urls)),
]

