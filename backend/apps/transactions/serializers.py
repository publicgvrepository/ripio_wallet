from django.db import transaction
from decimal import Decimal
from rest_framework import serializers
from apps.transactions.models import Transactions, TransactionDetail, UserWallet, Currency


class TransactionDetailSerializer(serializers.ModelSerializer):
    currency = serializers.CharField(source='currency.currency')

    class Meta:
        model = TransactionDetail
        fields = ('id', 'description', 'amount', 'currency')


class TransactionSerializer(serializers.ModelSerializer):
    username_from = serializers.CharField(source='user_from.username')
    username_to = serializers.CharField(source='user_to.username')
    detail = serializers.SerializerMethodField()

    class Meta:
        model = Transactions
        fields = ('username_from', 'username_to', 'date_transaction', 'detail')

    def get_detail(self, obj):
        serializer = TransactionDetailSerializer(obj.transactiondetail_set.all().first())
        return serializer.data


class TransactionCreateSerializer(serializers.ModelSerializer):
    username_to = serializers.CharField(max_length=100)
    currency_id = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))

    class Meta:
        model = TransactionDetail
        fields = ('username_to', 'currency_id', 'amount', 'description')

    def validate(self, data):
        current_user_id = self.context.get('user_id')
        currency_id = data.get('currency_id')
        amount = data.get('amount')

        if not Currency.objects.filter(currency=currency_id).exists():
            raise serializers.ValidationError({"currency_error": "No existe la moneda en los registros"})

        current_user_wallet = UserWallet.objects.filter(owner__id=current_user_id).first()
        user_to_wallet = UserWallet.objects.filter(owner__username=data.get('username_to')).first()

        if user_to_wallet is None:
            raise serializers.ValidationError({"error": "No existe el destinatario o su wallet"})

        if current_user_wallet.id == user_to_wallet.id:
            raise serializers.ValidationError({"error": "No te puedes hacer autotransferencias"})

        if current_user_wallet is None:
            raise serializers.ValidationError({"wallet_error": "No tienes wallet registrada"})

        if not current_user_wallet.can_transfer(currency_id, amount):
            raise serializers.ValidationError({"wallet_error": "No tienes el saldo suficiente"})

        return data

    def create(self, validated_data):
        amount = validated_data.get('amount')
        current_user_id = self.context.get('user_id')
        currency = Currency.objects.get(currency=validated_data.get('currency_id'))

        current_user_wallet = UserWallet.objects.filter(owner__id=current_user_id).first()
        user_to_wallet = UserWallet.objects.filter(owner__username=validated_data.get('username_to')).first()

        with transaction.atomic():
            current_user_currency_detail = current_user_wallet.get_currency_detail(
                currency_id=validated_data.get('currency_id')
                )
            user_to_currency_detail = user_to_wallet.get_currency_detail(
                currency_id=validated_data.get('currency_id')
                )
            new_transaction = Transactions.objects.create(
                user_from=current_user_wallet.owner,
                user_to=user_to_wallet.owner
            )
            TransactionDetail.objects.create(
                transaction=new_transaction,
                currency=currency,
                description=validated_data.get('description'),
                amount=amount
            )
            current_user_currency_detail.amount -= Decimal(amount)
            user_to_currency_detail.amount += Decimal(amount)
            current_user_currency_detail.save()
            user_to_currency_detail.save()
        return new_transaction


class UserWalletDetailSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username')
    currencies = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserWallet
        fields = ('owner_name', 'currencies')

    def get_currencies(self, obj):
        return [detail.get_balance() for detail in obj.walletdetail_set.all()]
