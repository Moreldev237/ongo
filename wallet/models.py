import uuid
from django.db import models, transaction
from django.conf import settings


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet - {self.user.email}"

    # Créditer wallet
    def credit(self, amount, description=""):
        with transaction.atomic():
            self.balance += amount
            self.save()
            Transaction.objects.create(
                wallet=self,
                transaction_type="CREDIT",
                amount=amount,
                description=description
            )

    # Débiter wallet
    def debit(self, amount, description=""):
        with transaction.atomic():
            if self.balance < amount:
                raise ValueError("Solde insuffisant")
            self.balance -= amount
            self.save()
            Transaction.objects.create(
                wallet=self,
                transaction_type="DEBIT",
                amount=amount,
                description=description
            )


class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"
    

class Promotion(models.Model):
    PROMO_TYPE = (
        ('CASHBACK', 'Cashback'),
        ('DISCOUNT', 'Discount'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    promo_type = models.CharField(max_length=10, choices=PROMO_TYPE)
    value = models.DecimalField(max_digits=5, decimal_places=2)  # %
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)