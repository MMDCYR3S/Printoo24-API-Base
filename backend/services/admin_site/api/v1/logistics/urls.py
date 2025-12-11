from django.urls import path
from .views import (
    CreateShipmentView,
    ShipmentDetailView,
    AddLogisticCostView,
    UpdateShipmentStatusView
)

urlpatterns = [
    path("", CreateShipmentView.as_view(), name="create-shipment"),
    path("<int:shipment_id>/", ShipmentDetailView.as_view(), name="shipment-detail"),
    path("add/<int:shipment_id>/", AddLogisticCostView.as_view(), name="add-logistic-cost"),
    path("update/<int:shipment_id>/", UpdateShipmentStatusView.as_view(), name="update-shipment-status"),
]

