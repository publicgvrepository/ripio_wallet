import pytest
from decimal import Decimal
from django.urls import reverse
from freezegun import freeze_time
from rest_framework.test import APIClient
from apps.users.models import CustomUser
from apps.transactions.models import UserWallet, Transactions


class TestTransactionCreate:

    def test_bad_request_no_jwt(self):
        client = APIClient()
        url = reverse('transactions-api')
        data = {}
        response = client.post(url, data=data, format='json')
        assert response.status_code == 401
        assert response.json() == {'detail': 'Las credenciales de autenticación no se proveyeron.'}

    @pytest.mark.parametrize(
        'data,expected',
        [
            (
                {},
                {
                    'amount': ['Este campo es requerido.'],
                    'currency_id': ['Este campo es requerido.'],
                    'description': ['Este campo es requerido.'],
                    'username_to': ['Este campo es requerido.']
                }
            ),
            (
                {
                    'username_to': 'usuario_a',
                    'currency_id': 'ARS',
                    'amount': '200',
                    'description': 'una descripción'
                },
                {
                    'error': ['No te puedes hacer autotransferencias']
                }
            ),
            (
                {
                    'username_to': 'usuario_z',
                    'currency_id': 'ARS',
                    'amount': '200',
                    'description': 'una descripción'
                },
                {
                    'error': ['No existe el destinatario o su wallet']
                }
            ),
            (
                {
                    'username_to': 'usuario_b',
                    'currency_id': 'URSS',
                    'amount': '200',
                    'description': 'una descripción'
                },
                {
                    'currency_error': ['No existe la moneda en los registros']
                }
            ),
            (
                {
                    'username_to': 'usuario_b',
                    'currency_id': 'ARS',
                    'amount': '900',
                    'description': 'una descripción'
                },
                {
                    'wallet_error': ['No tienes el saldo suficiente']
                }
            ),
            (
                {
                    'username_to': 'usuario_b',
                    'currency_id': 'ARS',
                    'amount': '0',
                    'description': 'una descripción'
                },
                {
                    'amount': ['Asegúrese de que este valor es mayor o igual a 0.01.']
                }
            ),
            (
                {
                    'username_to': 'usuario_b',
                    'currency_id': 'ARS',
                    'amount': '-33',
                    'description': 'una descripción'
                },
                {
                    'amount': ['Asegúrese de que este valor es mayor o igual a 0.01.']
                }
            ),
        ]
    )
    def test_bad_request(self, mocker, db, data, expected):
        """
        GIVEN: cliente válido
        WHEN: no manda datos en el body
        THEN: error 400, campos obligatorios

        GIVEN: cliente válido
        WHEN: intenta hacerse una transferencia a sí mismo
        THEN: error 400, No te puedes hacer autotransferencias

        GIVEN: cliente válido
        WHEN: intenta hacerse una transferencia a usuario no registrado
        THEN: error 400, No existe el destinatario o su wallet

        GIVEN: cliente válido
        WHEN: intenta hacerse una transferencia con moneda no registrada
        THEN: error 400, No existe la moneda en los registros

        GIVEN: cliente válido transaccion en pesos
        WHEN: monto superior al que puede transferir
        THEN: error 400, No tienes el saldo suficiente

        GIVEN: cliente válido transaccion en pesos
        WHEN: monto 0 o monto negativo
        THEN: error 400, Asegúrese de que este valor es mayor o igual a 0.01
        """
        user = CustomUser.objects.get(username='usuario_a')
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('transactions-api')
        data = data
        response = client.post(url, data=data, format='json')
        assert response.status_code == 400
        assert response.json() == expected

    @pytest.mark.parametrize(
        'data,expected',
        [
            (
                {
                    'username_to': 'usuario_b',
                    'currency_id': 'ARS',
                    'amount': '33',
                    'description': 'una descripción'
                },
                {}
            ),
            (
                {
                    'username_to': 'usuario_b',
                    'currency_id': 'ARS',
                    'amount': '899',
                    'description': 'una descripción'
                },
                {}
            )
        ]
    )
    @freeze_time("2022-05-20 12:00:00")
    def test_transaction_ok(self, mocker, db, data, expected):
        user = CustomUser.objects.get(username='usuario_a')
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('transactions-api')
        data = data

        previous_amount = UserWallet.objects.get(owner=user
            ).walletdetail_set.get(currency__currency=data.get('currency_id')).amount
        receiver_previous_amount = UserWallet.objects.get(owner__username=data.get('username_to')
            ).walletdetail_set.get(currency__currency=data.get('currency_id')).amount

        response = client.post(url, data=data, format='json')

        current_amount = UserWallet.objects.get(owner=user
            ).walletdetail_set.get(currency__currency=data.get('currency_id')).amount
        receiver_current_amount = UserWallet.objects.get(owner__username=data.get('username_to')
            ).walletdetail_set.get(currency__currency=data.get('currency_id')).amount

        new_transaction = Transactions.objects.get(id=response.json().get('id'))

        assert response.status_code == 201
        assert response.json().get('msj') == 'Transacción exitosa.'
        assert new_transaction is not None
        assert new_transaction.user_from == user
        assert new_transaction.user_to.username == data.get('username_to')
        assert current_amount == previous_amount - Decimal(data.get('amount'))
        assert receiver_current_amount == receiver_previous_amount + Decimal(data.get('amount'))
