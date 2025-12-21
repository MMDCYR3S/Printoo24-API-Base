from django.db import models

# ========== Base QuerySet ========== #
class BaseQuerySet(models.QuerySet):
    def get_by_id(self, id: int):
        return self.filter(id=id).first()