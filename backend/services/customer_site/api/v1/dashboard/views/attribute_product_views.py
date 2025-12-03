from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core.domain.product import (
    SizeDomainService,
    MaterialDomainService,
    QuantityDomainService,
    FileUploadSpecDomainService
)
from ..serializers import (
    SizeSerializer,
    MaterialSerializer,
    QuantitySerializer,
    FileUploadSpecSerializer
)

# ===== Size ViewSet ===== #
@extend_schema(tags=['Dashboard-Size'])
class SizeViewSet(viewsets.ViewSet):
    """
    مدیریت سایزها توسط ادمین.
    """
    serializer_class = SizeSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SizeDomainService()

    @extend_schema(responses=SizeSerializer(many=True))
    def list(self, request):
        queryset = self.service.get_all()
        serializer = SizeSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=SizeSerializer, responses=SizeSerializer)
    def create(self, request):
        serializer = SizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # ===== انتقال لاجیک ذخیره‌سازی به سرویس ===== #
        instance = self.service.create_size(serializer.validated_data)
        
        return Response(SizeSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        serializer = SizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        instance = self.service.update_size(pk, serializer.validated_data)
        return Response(SizeSerializer(instance).data)

    def destroy(self, request, pk=None):
        self.service.delete_size(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===== Material ViewSet ===== #
@extend_schema(tags=['Dashboard-Material'])
class MaterialViewSet(viewsets.ViewSet):
    """
    مدیریت متریال‌ها (جنس کاغذ/بنر و...) توسط ادمین.
    """
    serializer_class = MaterialSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = MaterialDomainService()

    @extend_schema(responses=MaterialSerializer(many=True))
    def list(self, request):
        # ادمین همه را می‌بیند (چه فعال چه غیرفعال)
        queryset = self.service.get_all(only_active=False)
        serializer = MaterialSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=MaterialSerializer, responses=MaterialSerializer)
    def create(self, request):
        serializer = MaterialSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        instance = self.service.create_material(serializer.validated_data)
        
        return Response(MaterialSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        serializer = MaterialSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        instance = self.service.update_material(pk, serializer.validated_data)
        return Response(MaterialSerializer(instance).data)

    def destroy(self, request, pk=None):
        self.service.delete_material(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

# ===== Quantity ViewSet ===== #
@extend_schema(tags=['Dashboard-Quantity'])
class QuantityViewSet(viewsets.ViewSet):
    """
    مدیریت مقادیر تیراژ (Master Data).
    """
    serializer_class = QuantitySerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = QuantityDomainService()

    @extend_schema(responses=QuantitySerializer(many=True))
    def list(self, request):
        queryset = self.service.get_all()
        serializer = QuantitySerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=QuantitySerializer, responses=QuantitySerializer)
    def create(self, request):
        serializer = QuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create_quantity(
            user=request.user, 
            value=serializer.validated_data['value']
        )
        return Response(QuantitySerializer(instance).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        self.service.delete_quantity(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===== File Upload Spec ViewSet ===== #
@extend_schema(tags=['Dashboard-FileUploadSpec'])
class FileUploadSpecViewSet(viewsets.ViewSet):
    """
    مدیریت انواع فایل‌های طراحی (لایه باز، خط برش و ...).
    """
    serializer_class = FileUploadSpecSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FileUploadSpecDomainService()

    @extend_schema(responses=FileUploadSpecSerializer(many=True))
    def list(self, request):
        queryset = self.service.get_all()
        serializer = FileUploadSpecSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=FileUploadSpecSerializer, responses=FileUploadSpecSerializer)
    def create(self, request):
        serializer = FileUploadSpecSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        instance = self.service.create_spec(serializer.validated_data)
        return Response(FileUploadSpecSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        serializer = FileUploadSpecSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        instance = self.service.update_spec(pk, serializer.validated_data)
        return Response(FileUploadSpecSerializer(instance).data)

    def destroy(self, request, pk=None):
        self.service.delete_spec(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    