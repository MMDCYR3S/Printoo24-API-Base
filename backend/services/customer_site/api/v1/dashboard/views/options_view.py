from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample

from core.product.services import OptionService
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
        self.service = OptionService()

    @extend_schema(responses=OptionSerializer(many=True))
    def list(self, request):
        queryset = self.service.get_all()
        serializer = OptionSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=OptionSerializer, 
        responses=OptionSerializer,
        description="ایجاد ویژگی به همراه مقادیر آن (Nested Creation).",
        examples=[
            OpenApiExample(
                'Create Option with Guide',
                summary='ایجاد ویژگی با راهنما و مقادیر',
                value={
                    "name": "paper_type",
                    "label": "جنس کاغذ",
                    "input_type": "select",
                    "guide_text": "لطفاً کاغذ مناسب با نوع چاپ انتخاب کنید.",
                    "guide_type": "info",
                    "values": [
                        {
                            "label": "گلاسه ۱۳۵ گرم",
                            "value": "glossy_135",
                            "guide_text": "اقتصادی‌ترین گزینه",
                            "guide_type": "tip"
                        },
                        {
                            "label": "کتان ۳۰۰ گرم",
                            "value": "linen_300",
                            "guide_text": "مناسب کارت‌های مدیریتی",
                            "guide_type": "info"
                        }
                    ]
                }
            )
        ]
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
        """ ویرایش کامل ویژگی و مقادیر آن (Smart Sync) """
        serializer = OptionSerializer(data=request.data, partial=True) # partial=True برای انعطاف بیشتر
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        # ===== مقادیر فرزندان ===== #
        values_data = data.pop('global_values', None)

        instance = self.service.update_full_option(pk, data, values_data)
        
        return Response(OptionSerializer(instance).data)

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
