from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.logistics.services import WarehouseAppService
from apps.permissions import AppPermissionChecker
from .serializers import (
    CreateShipmentInputSerializer,
    UpdateShipmentInputSerializer,
    ShipmentStatusInputSerializer,
    ShipmentOutputSerializer,
    CreateLogisticCostReportInputSerializer,
)

# ===== 1. ایجاد مرسوله و بسته‌ها (POST /api/v1/orders/{pk}/shipments/) =====
@extend_schema(tags=['Warehouse - Shipment'], 
               summary='عملیات بسته‌بندی: ایجاد مرسوله و بسته‌های اولیه')
class CreateShipmentView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateShipmentInputSerializer 
    
    def post(self, request, order_pk):
        AppPermissionChecker.check_has_permission(request.user, 'logistic.add_shipment')
        
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

    # متد GET برای نمایش جزئیات (از ShipmentRepository استفاده می‌کند)
    def get(self, request, pk):
        # [توجه]: دسترسی مشاهده باید با view_shipment چک شود
        AppPermissionChecker.check_has_permission(request.user, 'logistic.view_shipment') 
        
        # فرض می‌کنیم متد get_shipment_with_details در سرویس دامنه وجود دارد
        shipment = WarehouseAppService()._logistic_domain.get_shipment_with_details(pk)
        if not shipment:
            return Response({"detail": "مرسوله یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(ShipmentOutputSerializer(shipment).data, status=status.HTTP_200_OK)

    # متد PATCH برای به‌روزرسانی جزئیات
    def patch(self, request, pk):
        AppPermissionChecker.check_has_permission(request.user, 'logistic.change_shipment')
        
        serializer = UpdateShipmentInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        service = WarehouseAppService()
        shipment = service.update_shipment(
            user=request.user, 
            shipment_id=pk, 
            data=serializer.validated_data
        )
        
        return Response(ShipmentOutputSerializer(shipment).data, status=status.HTTP_200_OK)

# ===== 3. تغییر وضعیت مرسوله (POST /api/v1/shipments/{pk}/status/) =====
@extend_schema(tags=['Warehouse - Shipment'], 
               summary='تغییر وضعیت مرسوله (تحویل به متصدی، تحویل مشتری)')
class UpdateShipmentStatusView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShipmentStatusInputSerializer
    
    def post(self, request, pk):
        AppPermissionChecker.check_has_permission(request.user, 'logistic.change_shipment_status')
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = WarehouseAppService()
        
        shipment = service.change_shipment_status(
            user=request.user, 
            shipment_id=pk, 
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
        AppPermissionChecker.check_has_permission(request.user, 'logistic.add_cost_report')
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = WarehouseAppService()
        
        cost_report = service.add_logistic_cost_report(
            user=request.user, 
            order_id=order_pk, 
            data=serializer.validated_data
        )
        
        return Response(CostReportOutputSerializer(cost_report).data, status=status.HTTP_201_CREATED)
