class ProductNotFoundException(Exception):
    """ استثنا برای زمانی که محصول یافت نشد """
    pass

class ProductAlreadyExistsException(Exception):
    """ استثنا برای زمانی که محصول از قبل وجود دارد """
    pass

class InvalidProductDataException(Exception):
    """ استثنا برای زمانی که داده‌های محصول نامعتبر است """
    pass