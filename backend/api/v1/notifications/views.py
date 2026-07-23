from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes

from core.infrastructure.messages import msg_provider
from apps.notification.services import NotificationAppService
from .serializers import NotificationSerializer, NotificationListResponseSerializer

# ===== Notification List View ===== #
@extend_schema(tags=["Notification"])
class NotificationListView(APIView):
    """لیست تمام اعلان‌ها و تعداد ناخوانده‌ها"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="لیست اعلان‌ها",
        description="""
        این متد علاوه بر لیست اعلان‌ها، تعداد پیام‌های ناخوانده (`unread_count`) را نیز برمی‌گرداند تا بتوانید Badge قرمز رنگ را در هدر سایت آپدیت کنید.
        
        **کاربرد target_model و object_id:**
        فرانت می‌تواند با استفاده از این دو فیلد، کاربر را به صفحه درست هدایت کند.
        * اگر `target_model` برابر `order` بود -> لینک به `/orders/{object_id}`
        * اگر `target_model` برابر `ticket` بود -> لینک به `/tickets/{object_id}`
        """,
        responses={200: NotificationListResponseSerializer},
        examples=[
            OpenApiExample(
                'Notification Response',
                summary='مثال لیست اعلان‌ها',
                value={
                    "unread_count": 3,
                    "results": [
                        {
                            "id": 105,
                            "name": "تغییر وضعیت سفارش",
                            "message": "سفارش شما با کد 2050 به مرحله 'چاپ' وارد شد.",
                            "is_read": False,
                            "created_at": "2024-03-10T14:30:00Z",
                            "time_since": "10 دقیقه",
                            "target_model": "order",
                            "object_id": 2050
                        },
                        {
                            "id": 102,
                            "name": "شارژ کیف پول",
                            "message": "مبلغ ۵۰۰,۰۰۰ تومان به کیف پول شما اضافه شد.",
                            "is_read": True,
                            "created_at": "2024-03-09T10:00:00Z",
                            "time_since": "1 روز, 4 ساعت",
                            "target_model": "wallettransaction",
                            "object_id": 85
                        }
                    ]
                }
            )
        ]
    )
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

    @extend_schema(
        summary="خوانده شدن تکی",
        description="زمانی که کاربر روی یک اعلان کلیک می‌کند یا آن را می‌بندد، این متد را صدا بزنید.",
        responses={200: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Success Response',
                value={"detail": "اعلان خوانده شد."}
            )
        ]
    )
    def post(self, request, pk):
        service = NotificationAppService(request.user)
        service.mark_as_read(pk)
        return Response({"message": msg_provider.get("notification.S6006")}, status=status.HTTP_200_OK)

# ===== Notification Read All View ===== #
@extend_schema(tags=["Notification"])
class NotificationReadAllView(APIView):
    """خواندن تمام اعلان‌ها"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="خوانده شدن همه",
        description="معمولاً دکمه‌ای با عنوان 'Mark all as read' در رابط کاربری وجود دارد که این API را صدا می‌زند.",
        responses={200: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Success Response',
                value={"detail": "تمام اعلان‌ها خوانده شدند."}
            )
        ]
    )
    def post(self, request):
        service = NotificationAppService(request.user)
        service.mark_all_read()
        return Response({"message": msg_provider.get("notification.S6007")}, status=status.HTTP_200_OK)
