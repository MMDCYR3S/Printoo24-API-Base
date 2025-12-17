from rest_framework.generics import RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.operations.services import OrderScheduleAppService
from ..serializers import OrderScheduleSerializer

# ========== SCHEDULE VIEW ========== #
@extend_schema(tags=['Order - Schedule'])
class OrderScheduleManageView(GenericAPIView):
    """
    مدیریت زمان‌بندی سفارش.
    - POST: ایجاد زمان‌بندی جدید
    - PUT: ویرایش زمان‌بندی موجود
    - GET: مشاهده
    - DELETE: حذف
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderScheduleSerializer

    def get(self, request, pk):
        """ مشاهده زمان‌بندی """
        service = OrderScheduleAppService()
        try:
            schedule = service.get_schedule(request.user, pk)
            serializer = self.get_serializer(schedule)
            return Response(serializer.data)
        except Exception as e:
            # اگر وجود نداشت 404 بدهد
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
        """ 
        ایجاد زمان‌بندی جدید.
        اگر قبلاً وجود داشته باشد ارور 400 می‌دهد.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = OrderScheduleAppService()
            schedule = service.create_schedule(
                requester=request.user,
                order_id=pk,
                data=serializer.validated_data
            )
            return Response(self.get_serializer(schedule).data, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """ 
        ویرایش زمان‌بندی موجود.
        اگر وجود نداشته باشد ارور 404 می‌دهد.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = OrderScheduleAppService()
            schedule = service.update_schedule(
                requester=request.user,
                order_id=pk,
                data=serializer.validated_data
            )
            return Response(self.get_serializer(schedule).data, status=status.HTTP_200_OK)
            
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """ حذف زمان‌بندی """
        service = OrderScheduleAppService()
        try:
            service.delete_schedule(request.user, pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
