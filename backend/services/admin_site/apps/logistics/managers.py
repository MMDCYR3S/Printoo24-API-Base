from django.db import models

# ========== Base QuerySet ========== #
class BaseQuerySet(models.QuerySet):
    def get_by_id(self, id: int):
        return self.filter(id=id).first()

# ========== SHIPMENT QUERYSET ========== #
class ShipmentQuerySet(BaseQuerySet):
    """
    کوئری‌های مربوط به مرسوله‌های سفارش
    """
    def get_shipment_with_details(self, shipment_id: int):
        """ دریافت یک مرسوله با تمام جزئیات مربوطه (آدرس، متد، بسته‌ها) """
        return self.prefetch_related('packages').filter(id=shipment_id).first()
    
    def get_by_id(self, pk: int):
        return self.filter(pk=pk).first()

# ========== SHIPMENT MANAGERS ========== #
class ShipmentManager(models.Manager):
    def get_queryset(self):
        return ShipmentQuerySet(self.model, using=self._db)

    def get_shipment_with_details(self, shipment_id: int):
        return self.get_queryset().get_shipment_with_details(shipment_id)
    
    def get_by_id(self, pk: int):
        return self.get_queryset().get_by_id(pk)


# ========== PACKAGE MANAGERS ========== #
class PackageManager(models.Manager):
    """ مدیریت بسته‌های داخل مرسوله """
    pass
