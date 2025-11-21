from django.urls import path, include

app_name = "v1"

urlpatterns = [
    path("accounts/", include("api.v1.accounts.urls")),
    path("shop/", include("api.v1.shop.urls")),
    path("cart/", include("api.v1.cart.urls")),
    path("order/", include("api.v1.order.urls"))
]
