from typing import Dict, Any, List, Optional
from django.db.models import QuerySet
from core.utils.base_repository import BaseRepository
from core.models import Role

class RoleRepository(BaseRepository[Role]):
    def __init__(self):
        super().__init__(Role)

    def get_all_roles(self) -> QuerySet[Role]:
        return self.model.objects.all().prefetch_related('permissions').order_by('id')

    def get_role_by_code(self, code: str) -> Optional[Role]:
        return self.model.objects.filter(code=code).first()

    def create_role(self, data: Dict[str, Any]) -> Role:
        return self.model.objects.create(**data)

    def update_permissions(self, role: Role, permission_ids: List[int]):
        role.permissions.set(permission_ids)
