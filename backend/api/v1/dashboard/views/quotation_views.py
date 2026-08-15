from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.dashboard.services.quotation_service import QuotationDashboardService
from ..serializers.quotation_serializers import (
    QuotationSerializer,
    QuotationCreateSerializer,
    QuotationUpdateSerializer,
    QuotationStatusChangeSerializer,
)


@extend_schema(tags=["Admin - Quotation Management"])
class QuotationDashboardViewSet(viewsets.ViewSet):
    """
    مدیریت پیش‌فاکتورها توسط ادمین
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = QuotationDashboardService()

    @extend_schema(summary="لیست پیش‌فاکتورها", responses=QuotationSerializer(many=True))
    def list(self, request):
        queryset = self.service.get_quotation_list()
        serializer = QuotationSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(summary="جزئیات پیش‌فاکتور", responses=QuotationSerializer)
    def retrieve(self, request, pk=None):
        try:
            quotation = self.service.get_quotation_detail(pk)
            return Response(QuotationSerializer(quotation).data)
        except NotFound as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="ایجاد پیش‌فاکتور از روی سفارش",
        request=QuotationCreateSerializer,
        responses={201: QuotationSerializer},
    )
    def create(self, request):
        serializer = QuotationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            quotation = self.service.create_quotation(serializer.validated_data, request.user)
            return Response(QuotationSerializer(quotation).data, status=status.HTTP_201_CREATED)
        except (ValidationError, NotFound) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="ویرایش پیش‌فاکتور",
        request=QuotationUpdateSerializer,
        responses={200: QuotationSerializer},
    )
    def partial_update(self, request, pk=None):
        serializer = QuotationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            quotation = self.service.update_quotation(pk, serializer.validated_data)
            return Response(QuotationSerializer(quotation).data)
        except (NotFound, ValidationError) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="حذف پیش‌فاکتور")
    def destroy(self, request, pk=None):
        try:
            self.service.delete_quotation(pk)
            return Response({"detail": "پیش‌فاکتور حذف شد."}, status=status.HTTP_204_NO_CONTENT)
        except NotFound as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="تأیید پیش‌فاکتور",
        responses={200: QuotationSerializer},
    )
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        try:
            quotation = self.service.approve_quotation(pk)
            return Response(QuotationSerializer(quotation).data)
        except NotFound as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="تغییر وضعیت پیش‌فاکتور",
        request=QuotationStatusChangeSerializer,
        responses={200: QuotationSerializer},
    )
    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        serializer = QuotationStatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']
        try:
            quotation = self.service.change_status(pk, new_status)
            return Response(QuotationSerializer(quotation).data)
        except (NotFound, ValidationError) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
