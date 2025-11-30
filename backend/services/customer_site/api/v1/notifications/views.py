from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.notification.services import NotificationAppService
from .serializers import NotificationSerializer

# ===== Notification List View ===== #
@extend_schema(tags=["Notification"])
class NotificationListView(APIView):
    """لیست تمام اعلان‌ها و تعداد ناخوانده‌ها"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = NotificationAppService(request.user)
        notifications = service.get_my_notifications()
        unread_count = service.get_unread_count()
        
        serializer = NotificationSerializer(notifications, many=True)
        
        return Response({
            "unread_count": unread_count,
            "results": serializer.data
        })

# ===== Notification Read View ===== #
@extend_schema(tags=["Notification"])
class NotificationReadView(APIView):
    """خواندن یک اعلان خاص"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        service = NotificationAppService(request.user)
        service.mark_as_read(pk)
        return Response({"detail": "اعلان خوانده شد."}, status=status.HTTP_200_OK)

# ===== Notification Read All View ===== #
@extend_schema(tags=["Notification"])
class NotificationReadAllView(APIView):
    """خواندن تمام اعلان‌ها"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        service = NotificationAppService(request.user)
        service.mark_all_read()
        return Response({"detail": "تمام اعلان‌ها خوانده شدند."}, status=status.HTTP_200_OK)
