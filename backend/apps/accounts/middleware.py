from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AutoLoginSuperuserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            try:
                superuser = User.objects.filter(is_superuser=True).first()
                if superuser:
                    request.user = superuser
                    if 'HTTP_AUTHORIZATION' not in request.META:
                        refresh = RefreshToken.for_user(superuser)
                        request.META['HTTP_AUTHORIZATION'] = f'Bearer {str(refresh.access_token)}'
            except Exception:
                pass
