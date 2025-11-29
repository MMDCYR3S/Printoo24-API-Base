class WalletNotFoundException(Exception):
    """کیف پول یافت نشد"""
    pass

class InsufficientFundsException(Exception):
    """موجودی کافی نیست"""
    pass