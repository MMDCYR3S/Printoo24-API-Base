class CartNotFoundException(Exception):
    """وقتی سبد خرید پیدا نمی‌شود"""
    pass

class ItemNotFoundException(Exception):
    """وقتی آیتم در سبد نیست یا متعلق به کاربر نیست"""
    pass

class InvalidQuantityException(Exception):
    """تعداد نامعتبر (صفر یا منفی)"""
    pass