from django.urls import path
from .views import (
    NotificationListView,
    NotificationReadView,
    NotificationReadAllView
)

urlpatterns = [
    path("list/", NotificationListView.as_view(), name="notification-list"),
    path("read/<int:pk>/", NotificationReadView.as_view(), name="notification-read"),
    path("read-all/", NotificationReadAllView.as_view(), name="notification-read-all"),
]
