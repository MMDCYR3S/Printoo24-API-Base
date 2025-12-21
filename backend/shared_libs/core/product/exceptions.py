# ========== CATEGORY EXCEPTIONS ========== #
class ProductCategoryNotFoundException(Exception):
    """استثنا برای زمانی که دسته‌بندی محصول یافت نشد."""
    pass

class InvalidProductCategoryException(Exception):
    """استثنا برای زمانی که دسته‌بندی محصول نامعتبر است."""
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

# ========== RATING EXCEPTIONS ========== #
class OverRatingNumberException(Exception):
    pass

class NotBuyerException(Exception):
    pass