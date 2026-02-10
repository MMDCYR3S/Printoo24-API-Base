from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.exceptions import ValidationError

from core.models import Province, City
from apps.dashboard.services import CustomerOrchestratorService
from ..serializers.general_serializers import (
    CustomerReadSerializer,
    CustomerWriteSerializer,
    ProvinceSerialzier,
    CitySerialzier,
)

# ===== Customer ViewSet ===== #
@extend_schema(
    tags=['Dashboard-Customer']
)
class CustomerViewSet(ViewSet):
    """
    مدیریت جامع مشتریان توسط ادمین.
    شامل ایجاد (با پروفایل و کیف پول)، ویرایش، حذف و عملیات گروهی.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CustomerOrchestratorService()

    # ===== لیست مشتریان ===== #
    @extend_schema(responses=CustomerReadSerializer(many=True))
    def list(self, request):
        queryset = self.service.get_customer_list()
        serializer = CustomerReadSerializer(queryset, many=True)
        return Response(serializer.data)

    # ===== دریافت جزئیات ===== #
    @extend_schema(responses=CustomerReadSerializer)
    def retrieve(self, request, pk=None):
        user = self.service.get_customer_detail(pk)
        serializer = CustomerReadSerializer(user)
        return Response(serializer.data)

    # ===== ایجاد مشتری جدید ===== #
    @extend_schema(request=CustomerWriteSerializer, responses=CustomerReadSerializer)
    def create(self, request):
        serializer = CustomerWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # انتقال تمام لاجیک به سرویس ارکستراتور
        try:
            user = self.service.create_customer(serializer.validated_data)
            output_serializer = CustomerReadSerializer(user)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== ویرایش مشتری ===== #
    @extend_schema(request=CustomerWriteSerializer, responses=CustomerReadSerializer)
    def update(self, request, pk=None):
        """ آپدیت کاربر با فیلدهای داخل سریالایزر """
        try:
            user_id = int(pk)
        except (ValueError, TypeError):
            return Response(
                {'detail': 'شناسه کاربر باید عددی باشد'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_instance = self.service.user_repo.get_customer_by_id(user_id)
        except ValidationError:
            return Response({'detail': 'کاربر یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerWriteSerializer(
            instance=user_instance, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            user = self.service.update_customer(user_id, serializer.validated_data)
            output_serializer = CustomerReadSerializer(user)
            return Response(output_serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== حذف مشتری ===== #
    def destroy(self, request, pk=None):
        self.service.delete_customer(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== تغییر وضعیت گروهی ===== #
    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(name='ids', type=list, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='active', type=bool, location=OpenApiParameter.QUERY)
        ]
    )
    @action(detail=False, methods=['patch'], url_path='bulk-status')
    def bulk_status(self, request):
        ids = request.data.get('ids', [])
        is_active = request.data.get('is_active', True)
        
        count = self.service.bulk_toggle_status(ids, is_active)
        return Response({'detail': f'{count} کاربر بروزرسانی شدند.'})

    # ===== حذف گروهی ===== #
    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(name='ids', type=list, location=OpenApiParameter.QUERY),
        ]
    )
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        self.service.bulk_delete(ids)
        return Response({'detail': 'کاربران انتخاب شده حذف شدند.'})

    # ===== Province + City ===== #
    @action(detail=False, methods=["get"], url_path='provinces')
    def provinces(self, request):
        provinces = Province.objects.all()
        serializer = ProvinceSerialzier(provinces, many=True, context={'request' : request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary='Get cities by province',
        description='Retrieve all cities for a specific province',
        parameters=[
            OpenApiParameter(
                name='province_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='ID of the province',
                required=True
            ),
        ],
        responses={
            200: CitySerialzier(many=True),
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        }
    )
    @action(detail=False, methods=["get"], url_path='cities')
    def cities(self, request):
        province_id = request.query_params.get('province_id')
        
        if not province_id:
            return Response(
                {"error": "province_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cities = City.objects.filter(province_id=province_id)
        serializer = CitySerialzier(cities, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

