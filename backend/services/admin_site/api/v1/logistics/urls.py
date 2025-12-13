from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CreateShipmentView,
    ShipmentDetailView,
    AddLogisticCostView,
    UpdateShipmentStatusView,
    DeliveryMethodViewSet
)

router = DefaultRouter()
router.register(r'delivery/method', DeliveryMethodViewSet, basename='shipment')

urlpatterns = [
    path("<int:order_pk>/", CreateShipmentView.as_view(), name="create-shipment"),
    path("detail/<int:shipment_id>/", ShipmentDetailView.as_view(), name="shipment-detail"),
    path("add/<int:order_pk>/", AddLogisticCostView.as_view(), name="add-logistic-cost"),
    path("update/<int:shipment_id>/", UpdateShipmentStatusView.as_view(), name="update-shipment-status"),
    # ===== Routers ===== #
    path('', include(router.urls)),
]

