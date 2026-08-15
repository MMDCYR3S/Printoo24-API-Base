from core.models import User
from apps.accounts.models import Wallet, WalletTransaction


class WalletAppService:
    """
    سرویس کیف پول مخصوص کاربر عادی (پروفایل)
    """

    def __init__(self, user: User):
        self.user = user

    def get_wallet_balance(self, user_id: int) -> Wallet:
        wallet, _ = Wallet.objects.get_or_create(user_id=user_id)
        return wallet

    def get_transaction_history(self, user_id: int):
        return WalletTransaction.objects.filter(user_id=user_id).order_by('-created_at')