from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.logistics.services import WarehouseAppService
from apps.logistics.models import OrderShipment
from .serializers import (
    CreateShipmentInputSerializer,
    UpdateShipmentInputSerializer,
    ShipmentStatusInputSerializer,
    ShipmentOutputSerializer,
    CreateLogisticCostReportInputSerializer,
    CostReportOutputSerializer,
    PackageInputSerializer,
    PackageOutputSerializer,
)

# ========== SHIPMENT VIEWSET ========== #
@extend_schema(tags=['Warehouse - Shipment'])
class ShipmentViewSet(viewsets.ViewSet):
    """
    مدیریت کامل مرسولات (Shipment) شامل CRUD و تغییر وضعیت.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="لیست تمام مرسولات",
        responses={200: ShipmentOutputSerializer(many=True)}
    )
    def list(self, request):
        queryset = OrderShipment.objects.all().select_related('order').prefetch_related('packages')
        serializer = ShipmentOutputSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="دریافت جزئیات مرسوله",
        responses={200: ShipmentOutputSerializer}
    )
    def retrieve(self, request, pk=None):
        service = WarehouseAppService()
        shipment = service.get_shipment_details(request.user, pk)
        return Response(ShipmentOutputSerializer(shipment).data)

    @extend_schema(
        summary="ایجاد مرسوله جدید برای یک سفارش",
        request=CreateShipmentInputSerializer,
        responses={201: ShipmentOutputSerializer},
    )
    def create(self, request):
        serializer = CreateShipmentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        order =  validated_data['order']
        
        service = WarehouseAppService()
        shipment = service.create_shipment_and_packages(
            user=request.user,
            order_id=order.id,
            data=validated_data
        )
        return Response(ShipmentOutputSerializer(shipment).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="ویرایش مرسوله (جزئیات ارسال)",
        request=UpdateShipmentInputSerializer,
        responses={200: ShipmentOutputSerializer}
    )
    def update(self, request, pk=None):
        serializer = UpdateShipmentInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        service = WarehouseAppService()
        shipment = service.update_shipment(
            user=request.user,
            shipment_id=pk,
            data=serializer.validated_data
        )
        return Response(ShipmentOutputSerializer(shipment).data)
    
    @extend_schema(summary="حذف مرسوله (اگر پیاده‌سازی شده باشد)")
    def destroy(self, request, pk=None):
        service = WarehouseAppService()
        shipment = service.delete_shipment(request.user, pk)
        return Response(shipment, status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        summary="تغییر وضعیت مرسوله",
        request=ShipmentStatusInputSerializer,
        responses={200: ShipmentOutputSerializer}
    )
    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        serializer = ShipmentStatusInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = WarehouseAppService()
        shipment = service.change_shipment_status(
            user=request.user,
            shipment_id=pk,
            new_status_code=serializer.validated_data['new_status_code']
        )
        return Response(ShipmentOutputSerializer(shipment).data)
    
    @action(detail=True, methods=["post"], url_path="approve-status")
    def change_status(self, request, pk=None):
        service = WarehouseAppService()
        shipment = service.approve_shipment_status(
            user=request.user,
            shipment_id=pk
        )
        return Response({"success": "سفارش با موفقیت تحویل داده شد"}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="افزودن یک بسته جدید به مرسوله موجود",
        request=PackageInputSerializer,
        responses={201: PackageOutputSerializer}
    )
    @action(detail=True, methods=['post'], url_path='add-package')
    def add_package(self, request, pk=None):
        serializer = PackageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = WarehouseAppService()
        package = service.add_package_to_shipment(
            user=request.user,
            shipment_id=pk,
            data=serializer.validated_data
        )
        return Response(PackageOutputSerializer(package).data, status=status.HTTP_201_CREATED)

# ========== LOGISTIC COSTS ========== #
@extend_schema(tags=['Warehouse - Costs'])
class LogisticCostViewSet(viewsets.ViewSet):
    """
    مدیریت گزارش‌های هزینه لجستیک
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="ثبت گزارش هزینه برای یک سفارش",
        request=CreateLogisticCostReportInputSerializer,
        responses={201: CostReportOutputSerializer},
        parameters=[OpenApiParameter(name='order_id', type=int, location=OpenApiParameter.QUERY, description='شناسه سفارش')]
    )
    def create(self, request):
        serializer = CreateLogisticCostReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_id = request.query_params.get('order_id')
        if not order_id:
             return Response({'detail': 'order_id param is required'}, status=status.HTTP_400_BAD_REQUEST)

        service = WarehouseAppService()
        report = service.add_logistic_cost_report(
            user=request.user,
            order_id=order_id,
            data=serializer.validated_data
        )
        return Response(CostReportOutputSerializer(report).data, status=status.HTTP_201_CREATED)
