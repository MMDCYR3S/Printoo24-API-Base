import logging
from decimal import Decimal

from django.db import transaction
from django.core.exceptions import ValidationError

from core.common.wallet import WalletRepository, WalletTransactionRepository

# ===== تعریف لاگر اختصاصی کیف پول با پیشوند userprofile ===== #
logger = logging.getLogger('userprofile.services.wallet')

# ===== Wallet Service ===== #
class WalletService:
    """
    سرویس مدیریت اطلاعات کیف پول کاربر.
    
    این سرویس وظیفه نمایش موجودی فعلی و تاریخچه تراکنش‌های مالی کاربر را بر عهده دارد.
    """
    
    def __init__(self):
        # ===== تزریق وابستگی‌های مخزن کیف پول و تراکنش ===== #
        self._wallet_repo = WalletRepository()
        self._trans_repo = WalletTransactionRepository()

    def get_wallet_balance(self, user_id: int):
        """
        دریافت موجودی فعلی کیف پول کاربر.
        """
        logger.info(f"Fetching wallet balance for User ID: {user_id}")
        
        try:
            wallet = self._wallet_repo.get_by_user(user_id)
            
            # لاگ کردن موجودی برای دیباگ (در محیط پروداکشن ممکن است حساس باشد، پس DEBUG استفاده می‌کنیم)
            if wallet:
                logger.debug(f"Wallet found for User ID: {user_id}. Balance: {wallet.decimal}")
            else:
                logger.warning(f"No wallet found for User ID: {user_id}")
                
            return wallet
        except Exception as e:
            logger.exception(f"Error fetching wallet for User ID: {user_id}")
            raise e
    
    def get_transaction_history(self, user_id: int):
        """
        دریافت تاریخچه تراکنش‌های مالی کاربر.
        """
        logger.info(f"Fetching transaction history for User ID: {user_id}")
        
        try:
            history = self._trans_repo.get_history_by_user(user_id)
            logger.info(f"Retrieved {history.count()} transactions for User ID: {user_id}")
            return history
        except Exception as e:
            logger.exception(f"Error fetching transactions for User ID: {user_id}")
            raise e
