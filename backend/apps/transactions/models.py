from decimal import Decimal
from django.db import models


class Transactions(models.Model):
    user_from = models.ForeignKey('users.CustomUser', related_name='user_from', on_delete=models.PROTECT)
    user_to = models.ForeignKey('users.CustomUser', related_name='user_to', on_delete=models.PROTECT)
    date_transaction = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"De {self.user_from.username}, para {self.user_to.username} {self.date_transaction}"


class Currency(models.Model):
    name = models.CharField(max_length=100)
    currency = models.CharField(max_length=10)

    def __str__(self) -> str:
        return f"{self.name} {self.currency}"


class TransactionDetail(models.Model):
    transaction = models.ForeignKey('Transactions', on_delete=models.PROTECT)
    currency = models.ForeignKey('Currency', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)


class UserWallet(models.Model):
    owner = models.ForeignKey('users.CustomUser', on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"Wallet from {self.owner.username}"

    def can_transfer(self, currency_id: str, amount: float) -> bool:
        """Indica si desde la Wallet se puede hacer una transferencia

        Args:
            currency_id (str): siglas de la currency
            amount (float): monto a transferir

        Returns:
            bool: true si el monto disponible en la wallet es mayo o igual
        """
        available_currency = self.walletdetail_set.filter(currency__currency=currency_id).first()
        available_amount = 0.0 if available_currency is None else available_currency.amount
        return available_amount >= amount

    def get_currency_detail(self, currency_id: str):
        """Retorna una instancia de walletdetail

        Args:
            currency_id (str): siglas de la currency

        Returns:
            WalletDetail: un WalletDetail or None
        """
        return self.walletdetail_set.filter(currency__currency=currency_id).first()


class WalletDetail(models.Model):
    wallet = models.ForeignKey('UserWallet', on_delete=models.PROTECT)
    currency = models.ForeignKey('Currency', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.wallet.owner.username} saldo: {self.currency.currency} {self.amount}"

    def substraction_amount(self, amount: float) -> None:
        self.amount -= Decimal(amount)

    def get_balance(self) -> str:
        return f"{self.currency.currency} {self.amount}"
