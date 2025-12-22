from django.db import models
from .base import BaseQuerySet

# ========== TRANSACTION QUERYSET ========== #
class TransactionQuerySet(BaseQuerySet):
    def get_pending_transactions(self):
        return self.select_related('invoice', 'user').filter(status='pending')
    
    def get_by_id(self, pk: int):
        return self.filter(pk=pk).first()

# ========== TRANSACTION MANAGER ========== #
class TransactionManager(models.Manager):
    def get_queryset(self):
        return TransactionQuerySet(self.model, using=self._db)

    def get_pending_transactions(self):
        return self.get_queryset().get_pending_transactions()
    
    def get_by_id(self, pk: int):
        return self.get_queryset().get_by_id(pk)
