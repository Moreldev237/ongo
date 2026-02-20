from django.urls import path
from .views import WalletDetailView, TransactionListView, PayRideView

urlpatterns = [
    path('', WalletDetailView.as_view(), name='wallet-detail'),
    path('transactions/', TransactionListView.as_view(), name='wallet-transactions'),
    path('pay-ride/', PayRideView.as_view(), name='pay-ride'),

    path('wallet/', WalletDetailView.as_view(), name='wallet-detail'),
    path('wallet/transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('wallet/pay/', PayRideView.as_view(), name='pay-ride'),
]
