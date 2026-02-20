from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import Wallet, Transaction, Promotion
from utilisateurs.models import User  # Ton modèle User
from django.db import transaction as db_transaction 
#bibliothèque pour gérer les transactions atomiques

from rest_framework import generics, permissions
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer, PayRideSerializer




class PayRideView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Body attendu:
        {
            "driver_id": 2,
            "amount": 5000,
            "passengers": 1,       # Nombre de passagers pour covoiturage
            "bags": 0,             # Nombre d'options bagages
            "promotion_id": null   # ID promotion cashback ou discount
        }
        """
        user_wallet = request.user.wallet
        driver_id = request.data.get("driver_id")
        amount = float(request.data.get("amount", 0))
        passengers = int(request.data.get("passengers", 1))
        bags = int(request.data.get("bags", 0))
        promo_id = request.data.get("promotion_id", None)

        # Vérifier chauffeur
        try:
            driver = User.objects.get(id=driver_id)
            driver_wallet = driver.wallet
        except User.DoesNotExist:
            return Response({"error": "Chauffeur introuvable"}, status=status.HTTP_404_NOT_FOUND)

        # 1️⃣ Options covoiturage
        if passengers > 1:
            reduction = 0.25
            amount = round(amount * (1 - reduction), 2)

        # 2️⃣ Options bagages
        if bags > 0:
            surcharge_bags = 0.10 * bags  # 10% par bagage
            amount = round(amount * (1 + surcharge_bags), 2)

        # 3️⃣ Promotion
        cashback_amount = 0
        if promo_id:
            try:
                promo = Promotion.objects.get(id=promo_id, active=True)
                if promo.promo_type == "CASHBACK":
                    cashback_amount = round(amount * (promo.value / 100), 2)
                elif promo.promo_type == "DISCOUNT":
                    amount = round(amount * (1 - promo.value / 100), 2)
            except Promotion.DoesNotExist:
                pass

        # 4️⃣ Commission plateforme
        platform_commission = round(amount * 0.15, 2)
        driver_amount = amount - platform_commission

        try:
            with db_transaction.atomic():
                # Débit utilisateur
                user_wallet.debit(amount, f"Paiement trajet vers {driver.email}")
                
                # Crédit chauffeur
                driver_wallet.credit(driver_amount, f"Revenu trajet de {request.user.email}")
                
                # Crédit plateforme (superuser)
                platform_wallet = Wallet.objects.get(user__is_superuser=True)
                platform_wallet.credit(platform_commission, f"Commission trajet {request.user.email} -> {driver.email}")

                # Crédit cashback MOVECoin utilisateur
                if cashback_amount > 0:
                    user_wallet.credit(cashback_amount, f"Cashback promotion {promo.name}")

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Paiement effectué avec succès",
            "amount_paid": amount,
            "user_balance": user_wallet.balance,
            "driver_balance": driver_wallet.balance,
            "platform_balance": platform_wallet.balance,
            "cashback_credited": cashback_amount
        })
    
    #2e phase de developpement 


# Détail du wallet de l'utilisateur connecté
class WalletDetailView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Wallet.objects.get(user=self.request.user)

# Liste des transactions du wallet
class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        wallet = Wallet.objects.get(user=self.request.user)
        return Transaction.objects.filter(wallet=wallet).order_by('-created_at')

# Simuler un paiement (réservation de trajet)
class PayRideView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = PayRideSerializer(data=request.data)
        if serializer.is_valid():
            # Exemple simple : on débite le wallet
            wallet = Wallet.objects.get(user=request.user)
            amount = serializer.validated_data['amount']
            if wallet.balance < amount:
                return Response({"detail": "Solde insuffisant"}, status=status.HTTP_400_BAD_REQUEST)
            wallet.balance -= amount
            wallet.save()
            # Créer une transaction
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='DEBIT',
                amount=amount,
                description=serializer.validated_data.get('description', 'Paiement trajet')
            )
            return Response({"detail": "Paiement effectué avec succès"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)