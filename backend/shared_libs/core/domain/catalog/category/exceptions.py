class ProductCategoryNotFoundException(Exception):
    """استثنا برای زمانی که دسته‌بندی محصول یافت نشد."""
    pass

class InvalidProductCategoryException(Exception):
    """استثنا برای زمانی که دسته‌بندی محصول نامعتبر است."""
    pass