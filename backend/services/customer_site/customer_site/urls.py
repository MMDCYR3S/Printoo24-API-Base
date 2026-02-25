"""
URL configuration for customer_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Printoo24 API Documentation",
      default_version='v1',
      description="مستندات جامع ای‌پی‌آی‌های وب‌سایت پرینتو ۲۴ برای تیم فرانت‌اند.",
      terms_of_service="https://www.printoo24.com/terms/",
      contact=openapi.Contact(email="developer@printoo24.com"),
      license=openapi.License(name="Private License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,), # فعلا برای توسعه باز می‌ذاریم تا فرانت‌اند راحت ببینه
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
