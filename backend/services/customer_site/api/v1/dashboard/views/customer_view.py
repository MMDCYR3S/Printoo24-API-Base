from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.exceptions import ValidationError

from apps.dashboard.services import CustomerOrchestratorService
from ..serializers.general_serializers import CustomerManagementSerializer

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
    @extend_schema(responses=CustomerManagementSerializer(many=True))
    def list(self, request):
        queryset = self.service.get_customer_list()
        serializer = CustomerManagementSerializer(queryset, many=True)
        return Response(serializer.data)

    # ===== دریافت جزئیات ===== #
    @extend_schema(responses=CustomerManagementSerializer)
    def retrieve(self, request, pk=None):
        user = self.service.get_customer_detail(pk)
        serializer = CustomerManagementSerializer(user)
        return Response(serializer.data)

    # ===== ایجاد مشتری جدید ===== #
    @extend_schema(request=CustomerManagementSerializer, responses=CustomerManagementSerializer)
    def create(self, request):
        serializer = CustomerManagementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # انتقال تمام لاجیک به سرویس ارکستراتور
        try:
            user = self.service.create_customer(serializer.validated_data)
            output_serializer = CustomerManagementSerializer(user)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== ویرایش مشتری ===== #
    @extend_schema(request=CustomerManagementSerializer, responses=CustomerManagementSerializer)
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

        serializer = CustomerManagementSerializer(
            instance=user_instance, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            user = self.service.update_customer(user_id, serializer.validated_data)
            output_serializer = CustomerManagementSerializer(user)
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
