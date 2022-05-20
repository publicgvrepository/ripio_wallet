from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.transactions.models import Transactions, UserWallet
from apps.transactions.serializers import TransactionSerializer, TransactionCreateSerializer, UserWalletDetailSerializer


class TransacionCreateView(generics.ListCreateAPIView):

    def get(self, request, format=None):
        transactions = Transactions.objects.filter(
            user_from__id=request.user.id
        )
        serializer = TransactionSerializer(
            transactions,
            many=True
        )
        return Response(serializer.data)

    @extend_schema(
        request=TransactionCreateSerializer
    )
    def post(self, request):
        transaction_serializer = TransactionCreateSerializer(
            data=request.data,
            context={
                'user_id': request.user.id
            }
        )
        if transaction_serializer.is_valid():
            new_transaction = transaction_serializer.save()
            return Response({'msj': 'Transacción exitosa.', 'id': new_transaction.id}, status=status.HTTP_201_CREATED)
        return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletRetrieveView(generics.GenericAPIView):

    def get(self, request, format=None):
        serializer = UserWalletDetailSerializer(UserWallet.objects.get(owner__id=request.user.id))
        return Response(serializer.data)
