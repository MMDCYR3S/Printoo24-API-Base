from django.urls import path, include

urlpatterns = [
    path("users/", include("api.v1.accounts.urls")),
    path("operations/", include("api.v1.operations.urls")),
    path("logistics/", include("api.v1.logistics.urls")),
    path("financial/", include("api.v1.financial.urls")),
    path("order/", include("api.v1.order.urls"))
]

