from django.contrib import admin
from apps.transactions.models import (
                                        Transactions,
                                        TransactionDetail,
                                        UserWallet,
                                        Currency,
                                        WalletDetail
                                    )

admin.site.register(Transactions)
admin.site.register(TransactionDetail)
admin.site.register(UserWallet)
admin.site.register(Currency)
admin.site.register(WalletDetail)
