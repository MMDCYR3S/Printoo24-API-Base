# ========== USER EXCEPTIONS ========== #
class EmailAlreadyExistsException(Exception):
    """استثنایی که زمانی رخ می‌دهد که ایمیل از قبل وجود داشته باشد."""
    pass

class EmailNotFoundException(Exception):
    """استثنایی که زمانی رخ می‌دهد که ایمیل پیدا نشود."""
    pass

class UsernameAlreadyExistsException(Exception):
    """استثنایی که زمانی رخ می‌دهد که نام کاربری از قبل وجود داشته باشد."""
    pass

class UsernameNotFoundException(Exception):
    """استثنایی که زمانی رخ می‌دهد که نام کاربری پیدا نشود."""
    pass

# ========== WALLET EXCEPTIONS ========== #
class WalletNotFoundException(Exception):
    """کیف پول یافت نشد"""
    pass

class InsufficientFundsException(Exception):
    """موجودی کافی نیست"""
    pass

