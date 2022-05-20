from django.contrib.auth.hashers import make_password
from django.db import transaction
from decimal import Decimal
from rest_framework import serializers
from apps.users.models import CustomUser
from apps.transactions.models import UserWallet, Currency, WalletDetail


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True)
    password = serializers.CharField(
        min_length=8)

    class Meta:
        model = CustomUser
        fields = ('username', 'password')

    def validate_password(self, value):
        return make_password(value)

    def create(self, validated_data):
        new_user = super().create(validated_data)
        with transaction.atomic():
            new_wallet = UserWallet.objects.create(
                owner=new_user
            )
            for currency in Currency.objects.all():
                WalletDetail.objects.create(
                    wallet=new_wallet,
                    currency=currency,
                    amount=Decimal(0)
                )
        return new_user
