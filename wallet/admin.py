from django.contrib import admin
from .models import Wallet, Transaction, Promotion

# Wallet : afficher solde et utilisateur
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'created_at', 'updated_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')  # on ne modifie pas ces champs directement

# Transaction : historique
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'description', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('wallet__user__email', 'description')
    readonly_fields = ('created_at',)

# Promotion : gérer cashback et discount
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'promo_type', 'value', 'active', 'created_at')
    list_filter = ('promo_type', 'active')
    search_fields = ('name',)
    readonly_fields = ('created_at',)