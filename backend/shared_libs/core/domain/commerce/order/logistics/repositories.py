from core.utils.base_repository import BaseRepository
from core.models import DeliveryMethod, OrderShipment, OrderPackage

# ====== Delivery Method Repository ====== #
class DeliveryMethodRepository(BaseRepository[DeliveryMethod]):
    """ مدیریت متدهای ارسال """
    def __init__(self):
        super().__init__(DeliveryMethod)

# ====== Order Shipment Repository ====== #
class ShipmentRepository(BaseRepository[OrderShipment]):
    """ مدیریت مرسوله‌های سفارش """
    def __init__(self):
        super().__init__(OrderShipment)

    def get_shipment_with_details(self, shipment_id: int):
        """ دریافت یک مرسوله با تمام جزئیات مربوطه (آدرس، متد، بسته‌ها) """
        return self.model.objects.select_related(
            'delivery_method', 
            'destination_address__city', 
            'destination_address__province'
        ).prefetch_related('packages').filter(id=shipment_id).first()

# ====== Order Package Repository ====== #
class PackageRepository(BaseRepository[OrderPackage]):
    """ مدیریت بسته‌های داخل مرسوله """
    def __init__(self):
        super().__init__(OrderPackage)
