# ========== CATEGORY EXCEPTIONS ========== #
class ProductCategoryNotFoundException(Exception):
    """استثنا برای زمانی که دسته‌بندی محصول یافت نشد."""
    pass

class InvalidProductCategoryException(Exception):
    """استثنا برای زمانی که دسته‌بندی محصول نامعتبر است."""
    pass

class ProductCategoryHasDependencyException(Exception):
    """استثنا برای زمانی که دسته‌بندی وابستگی دارد و قابل حذف نیست."""
    pass

# ========== PRODUCT EXCEPTIONS ========== #
class ProductNotFoundException(Exception):
    """ استثنا برای زمانی که محصول یافت نشد """
    pass

class ProductAlreadyExistsException(Exception):
    """ استثنا برای زمانی که محصول از قبل وجود دارد """
    pass

class InvalidProductDataException(Exception):
    """ استثنا برای زمانی که داده‌های محصول نامعتبر است """
    pass

class ProductHasDependencyException(Exception):
    """استثنا برای زمانی که محصول وابستگی دارد (مثلاً در سفارشات ثبت شده) و قابل حذف مستقیم نیست."""
    pass

# ========== RATING EXCEPTIONS ========== #
class OverRatingNumberException(Exception):
    pass

class NotBuyerException(Exception):
    pass

# ========== MEDIA EXCEPTIONS ========== #
class ProductImageNotFoundException(Exception):
    """استثنا برای زمانی که تصویر محصول یافت نشد."""
    pass

class AttachmentNotFoundException(Exception):
    """استثنا برای زمانی که فایل پیوست یافت نشد."""
    pass