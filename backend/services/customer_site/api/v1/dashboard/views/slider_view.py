from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from core.domain.general import SliderDomainService
from ..serializers import SliderDashboardSerializer

# ===== Slider Dashboard View Set ===== #
@extend_schema(tags=['Dashboard-Slider'])
class SliderDashboardViewSet(viewsets.ModelViewSet):
    """
    مدیریت اسلایدرهای صفحه اصلی (CRUD کامل).
    """
    serializer_class = SliderDashboardSerializer
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SliderDomainService()

    def get_queryset(self):
        return self.service.get_all()

    # ===== ایجاد اسلایدر ===== #
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file_obj = request.FILES.get('image')
        
        instance = self.service.create_slider(
            data=serializer.validated_data,
            file_obj=file_obj
        )
        
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

    # ===== ویرایش اسلایدر ===== #
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object() # یا self.service.get_detail(pk)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        file_obj = request.FILES.get('image')

        updated_instance = self.service.update_slider(
            pk=instance.pk,
            data=serializer.validated_data,
            file_obj=file_obj
        )

        return Response(self.get_serializer(updated_instance).data)

    # ===== حذف اسلایدر ===== #
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.delete_slider(instance.pk)
        return Response(status=status.HTTP_204_NO_CONTENT)