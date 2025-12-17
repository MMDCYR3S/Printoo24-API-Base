from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from core.domain.catalog.category import ProductCategoryDomainService
from ..serializers.general_serializers import ProductCategoryDashboardSerializer

# ===== ویو‌ست مدیریت دسته‌بندی‌ها ===== #
@extend_schema(tags=['Dashboard-Category-Banner'])
class ProductCategoryDashboardViewSet(ModelViewSet):
    """
    این ویو‌ست تمامی عملیات CRUD برای دسته‌بندی‌ها را مدیریت می‌کند.
    شامل: لیست، جزئیات، افزودن، ویرایش، حذف و عملیات گروهی.
    """
    serializer_class = ProductCategoryDashboardSerializer
    permission_classes = [IsAdminUser]
    
    # ===== تزریق وابستگی ===== #
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProductCategoryDomainService()

    # ===== بازنویسی متد get_queryset ===== #
    def get_queryset(self):
        return self.service.get_category_tree_queryset()
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # ===== بازنویسی متد create (افزودن) ===== #
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # پاس دادن داده‌های معتبر به سرویس دامین
        instance = self.service.create_category(serializer.validated_data)
        
        # سریالایز کردن مجدد برای پاسخ
        output_serializer = self.get_serializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    # ===== بازنویسی متد update (ویرایش) ===== #
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_instance = self.service.update_category(instance, serializer.validated_data)
        
        output_serializer = self.get_serializer(updated_instance)
        return Response(output_serializer.data)

    # ===== بازنویسی متد destroy (حذف) ===== #
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.delete_category(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== اکشن سفارشی: تغییر وضعیت گروهی ===== #
    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(name='ids', type=list, location=OpenApiParameter.QUERY, description='لیست شناسه ها'),
            OpenApiParameter(name='active', type=bool, location=OpenApiParameter.QUERY, description='وضعیت جدید')
        ],
        summary="تغییر وضعیت گروهی"
    )
    @action(detail=False, methods=['patch'], url_path='bulk-status')
    def bulk_status(self, request):
        ids = request.data.get('ids', [])
        is_active = request.data.get('is_active', True)
        
        if not ids:
            return Response({'detail': 'لیست شناسه (ids) الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)
            
        count = self.service.bulk_toggle_status(ids, is_active)
        return Response({'detail': f'{count} دسته‌بندی بروزرسانی شدند.'}, status=status.HTTP_200_OK)

    # ===== اکشن سفارشی: حذف گروهی ===== #
    @extend_schema(summary="حذف گروهی")
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
             return Response({'detail': 'لیست شناسه (ids) الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)
        
        self.service.bulk_delete(ids)
        return Response({'detail': 'موارد انتخاب شده حذف شدند.'}, status=status.HTTP_204_NO_CONTENT)
