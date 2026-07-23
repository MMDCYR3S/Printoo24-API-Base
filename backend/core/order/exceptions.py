class OrderNotFoundException(Exception):
    """سفارش مورد نظر یافت نشد."""
    pass

class InvalidOrderOperationException(Exception):
    """عملیات غیرمجاز روی سفارش (مثلا حذف سفارشی که فاکتور شده)."""
    pass