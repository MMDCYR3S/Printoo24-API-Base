from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from core.domain.catalog.product import OptionDomainService
from ..serializers import OptionSerializer, OptionValueSerializer

# ===== Option View Set ===== #
@extend_schema(tags=['Dashboard-Options'])
class OptionViewSet(viewsets.ViewSet):
    """
    مدیریت بانک ویژگی‌ها (Global Options).
    """
    serializer_class = OptionSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OptionDomainService()

    @extend_schema(responses=OptionSerializer(many=True))
    def list(self, request):
        queryset = self.service.get_all()
        serializer = OptionSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=OptionSerializer, 
        responses=OptionSerializer,
        description="ایجاد ویژگی به همراه مقادیر آن (Nested Creation)."
    )
    def create(self, request):
        # ===== اعتبارسنجی اولیه ===== #
        serializer = OptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        # ===== افزودن مقدار به ویژگی ===== #
        values_data = data.pop('global_values', [])
        
        # ===== شروع فراخوانی سرویس ===== #
        instance = self.service.create_full_option(data, values_data)
        
        # ===== پایان فراخوانی سرویس ===== #
        return Response(OptionSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """ویرایش فقط اطلاعات پایه ویژگی"""
        serializer = OptionSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        clean_data = {k: v for k, v in serializer.validated_data.items() if k != 'global_values'}
        
        instance = self.service.update_option(pk, clean_data)
        return Response(OptionSerializer(instance).data)

    def destroy(self, request, pk=None):
        self.service.delete_option(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== اکشن اختصاصی برای افزودن مقدار جدید ===== #
    @extend_schema(
        request=OptionValueSerializer,
        responses=OptionValueSerializer,
        summary="افزودن تک مقدار به ویژگی"
    )
    @action(detail=True, methods=['post'], url_path='add-value')
    def add_value(self, request, pk=None):
        serializer = OptionValueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        value_instance = self.service.add_value_to_option(pk, serializer.validated_data)
        return Response(OptionValueSerializer(value_instance).data, status=status.HTTP_201_CREATED)
