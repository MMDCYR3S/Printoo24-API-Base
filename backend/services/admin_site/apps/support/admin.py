from .models import AuditLog
from core.site import custom_admin_site

# ===== LOGGER ===== #
custom_admin_site.register(AuditLog)

