from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.dashboard.services.location_service import LocationDashboardService
from ..serializers.location_serializers import (
    ProvinceSerializer, 
    CitySerializer, 
    CityCreateUpdateSerializer, 
    BulkDeleteSerializer
)

# ===== Province Dashboard ===== #
@extend_schema(tags=['Dashboard-Provinces'])
class ProvinceDashboardViewSet(viewsets.ViewSet):
    """ مدیریت استان‌ها """
    permission_classes = [IsAdminUser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = LocationDashboardService()

    @extend_schema(responses=ProvinceSerializer(many=True))
    def list(self, request):
        queryset = self.service.get_all_provinces()
        serializer = ProvinceSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(responses=ProvinceSerializer)
    def retrieve(self, request, pk=None):
        try:
            province = self.service.get_province_detail(pk)
            return Response(ProvinceSerializer(province).data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(request=ProvinceSerializer, responses=ProvinceSerializer)
    def create(self, request):
        serializer = ProvinceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        province = self.service.create_province(serializer.validated_data)
        return Response(ProvinceSerializer(province).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=ProvinceSerializer, responses=ProvinceSerializer)
    def update(self, request, pk=None):
        serializer = ProvinceSerializer(data=request.data, partial=True) # Partial allowed
        serializer.is_valid(raise_exception=True)
        try:
            province = self.service.update_province(pk, serializer.validated_data)
            return Response(ProvinceSerializer(province).data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            self.service.delete_province(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=BulkDeleteSerializer, responses={200: None})
    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        serializer = BulkDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        count = self.service.bulk_delete_provinces(ids)
        return Response({'message': f'{count} استان حذف شد.'}, status=status.HTTP_200_OK)


# ===== City Dashboard ===== #
@extend_schema(tags=['Dashboard-Cities'])
class CityDashboardViewSet(viewsets.ViewSet):
    """ مدیریت شهرها """
    permission_classes = [IsAdminUser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = LocationDashboardService()

    @extend_schema(
        responses=CitySerializer(many=True),
        parameters=[OpenApiParameter(name='province_id', type=int, location=OpenApiParameter.QUERY)]
    )
    def list(self, request):
        province_id = request.query_params.get('province_id')
        if province_id:
            queryset = self.service.get_cities_by_province(province_id)
        else:
            queryset = self.service.get_all_cities()
            
        serializer = CitySerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(responses=CitySerializer)
    def retrieve(self, request, pk=None):
        try:
            city = self.service.get_city_detail(pk)
            return Response(CitySerializer(city).data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(request=CityCreateUpdateSerializer, responses=CitySerializer)
    def create(self, request):
        serializer = CityCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        city = self.service.create_city(serializer.validated_data)
        return Response(CitySerializer(city).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=CityCreateUpdateSerializer, responses=CitySerializer)
    def update(self, request, pk=None):
        serializer = CityCreateUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            city = self.service.update_city(pk, serializer.validated_data)
            return Response(CitySerializer(city).data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            self.service.delete_city(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=BulkDeleteSerializer, responses={200: None})
    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        serializer = BulkDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        count = self.service.bulk_delete_cities(ids)
        return Response({'message': f'{count} شهر حذف شد.'}, status=status.HTTP_200_OK)
    