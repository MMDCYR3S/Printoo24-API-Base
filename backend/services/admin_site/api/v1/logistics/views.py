from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.logistics.services import WarehouseAppService
from apps.permissions import AppPermissionChecker
from core.models import DeliveryMethod
from .serializers import (
    CostReportOutputSerializer,
    CreateShipmentInputSerializer,
    UpdateShipmentInputSerializer,
    ShipmentStatusInputSerializer,
    ShipmentOutputSerializer,
    CreateLogisticCostReportInputSerializer,
    DeliveryMethodSerializer,
)

# ===== 1. ایجاد مرسوله و بسته‌ها (POST /api/v1/orders/{pk}/shipments/) =====
@extend_schema(tags=['Warehouse - Shipment'], 
               summary='عملیات بسته‌بندی: ایجاد مرسوله و بسته‌های اولیه')
class CreateShipmentView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateShipmentInputSerializer 
    
    def post(self, request, order_pk):
        AppPermissionChecker.check_has_permission(request.user, 'add_ordershipment')
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = WarehouseAppService()
        
        shipment = service.create_shipment_and_packages(
            user=request.user, 
            order_id=order_pk, 
            data=serializer.validated_data
        )
        
        return Response(ShipmentOutputSerializer(shipment).data, status=status.HTTP_201_CREATED)

# ===== 2. به‌روزرسانی و مشاهده جزئیات مرسوله (PATCH /api/v1/shipments/{pk}/) =====
@extend_schema(tags=['Warehouse - Shipment'], 
               summary='مشاهده و به‌روزرسانی مرسوله (کد رهگیری، هزینه، آدرس)')
class ShipmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, shipment_id):
        AppPermissionChecker.check_has_permission(request.user, 'view_ordershipment') 
        
        shipment = WarehouseAppService()._logistic_domain.get_shipment_with_details(shipment_id)
        if not shipment:
            return Response({"detail": "مرسوله یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(ShipmentOutputSerializer(shipment).data, status=status.HTTP_200_OK)

    # ===== بروزرسانی مرسوله ===== #
    def patch(self, request, shipment_id):
        AppPermissionChecker.check_has_permission(request.user, 'change_ordershipment')
        
        serializer = UpdateShipmentInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        service = WarehouseAppService()
        shipment = service.update_shipment(
            user=request.user, 
            shipment_id=shipment_id, 
            data=serializer.validated_data
        )
        
        return Response(ShipmentOutputSerializer(shipment).data, status=status.HTTP_200_OK)

# ===== 3. تغییر وضعیت مرسوله (POST /api/v1/shipments/{pk}/status/) =====
@extend_schema(tags=['Warehouse - Shipment'], 
               summary='تغییر وضعیت مرسوله (تحویل به متصدی، تحویل مشتری)')
class UpdateShipmentStatusView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShipmentStatusInputSerializer
    
    def post(self, request, shipment_id):
        AppPermissionChecker.check_has_permission(request.user, 'change_ordershipment')
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = WarehouseAppService()
        
        shipment = service.change_shipment_status(
            user=request.user, 
            shipment_id=shipment_id, 
            new_status_code=serializer.validated_data['new_status_code']
        )
        
        return Response(ShipmentOutputSerializer(shipment).data, status=status.HTTP_200_OK)

# ===== 4. ثبت گزارش هزینه‌های لجستیک (POST /api/v1/orders/{pk}/logistic-costs/) =====
@extend_schema(tags=['Warehouse - Cost'], 
               summary='ثبت گزارش هزینه‌های متفرقه لجستیک (بیمه، بسته‌بندی اضافی)')
class AddLogisticCostView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateLogisticCostReportInputSerializer
    
    def post(self, request, order_pk):
        AppPermissionChecker.check_has_permission(request.user, 'add_ordercostreport')
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = WarehouseAppService()
        
        cost_report = service.add_logistic_cost_report(
            user=request.user, 
            order_id=order_pk, 
            data=serializer.validated_data
        )
        
        return Response(CostReportOutputSerializer(cost_report).data, status=status.HTTP_201_CREATED)

# ========== Delivery Method ========== #
@extend_schema(tags=['Warehouse - Method'])
class DeliveryMethodViewSet(ModelViewSet):
    """
    مدیریت روش‌های ارسال (پیک، پست، تیپاکس).
    فقط مدیران سیستم یا مدیران لجستیک باید دسترسی نوشتن داشته باشند.
    """
    permission_classes = [IsAuthenticated]
    queryset = DeliveryMethod.objects.all()
    serializer_class = DeliveryMethodSerializer

    def get_permissions(self):
        return super().get_permissions()

    def perform_create(self, serializer):
        AppPermissionChecker.check_has_permission(self.request.user, 'add_deliverymethod')
        serializer.save()

    def perform_update(self, serializer):
        AppPermissionChecker.check_has_permission(self.request.user, 'change_deliverymethod')
        serializer.save()

    def perform_destroy(self, instance):
        AppPermissionChecker.check_has_permission(self.request.user, 'delete_deliverymethod')
        instance.delete()
