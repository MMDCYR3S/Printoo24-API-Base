from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ShipmentViewSet,
    LogisticFinancialViewSet
)

router = DefaultRouter()
router.register(r'shipments', ShipmentViewSet, basename='shipment')
# router.register(r'costs', LogisticFinancialViewSet, basename='logistic-cost')

urlpatterns = [
    path('', include(router.urls)),
]

