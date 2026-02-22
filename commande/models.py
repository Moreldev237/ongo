from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta


class VehicleType(models.TextChoices):
    """Types de véhicules disponibles"""
    TAXI = 'taxi', '🚕 Taxi'
    MOTO = 'moto', '🏍️ Moto'
    SCOOTER = 'scooter', '🛵 Scooter'
    VAN = 'van', '🚐 Van'
    VIP = 'vip', '👑 VIP'
    CORBILLARD = 'corbillard', '⚰️ Corbillard'
    TRICYCLE = 'tricycle', '🛺 Tricycle'
    PICKUP = 'pickup', '🚘 Pickup'


class OrderStatus(models.TextChoices):
    """Statuts possibles d'une commande"""
    PENDING = 'pending', 'En attente ⏳'
    CONFIRMED = 'confirmed', 'Confirmée ✓'
    ACCEPTED = 'accepted', 'Acceptée par chauffeur 👨‍💼'
    DRIVER_ARRIVING = 'driver_arriving', 'Chauffeur en approche 🚗'
    DRIVER_ARRIVED = 'driver_arrived', 'Chauffeur arrivé 📍'
    IN_PROGRESS = 'in_progress', 'En cours 🚙'
    COMPLETED = 'completed', 'Complétée ✓'
    CANCELLED_USER = 'cancelled_user', 'Annulée (utilisateur) ✗'
    CANCELLED_DRIVER = 'cancelled_driver', 'Annulée (chauffeur) ✗'
    CANCELLED_ADMIN = 'cancelled_admin', 'Annulée (admin) ✗'
    NO_SHOW = 'no_show', 'Non présenté (no-show) 🚫'


class PaymentMethod(models.TextChoices):
    """Méthodes de paiement"""
    MOVECOIN = 'movecoin', 'MOVECoin'
    ORANGE_MONEY = 'orange_money', 'Orange Money'
    MTN_MONEY = 'mtn_money', 'MTN Money'
    CREDIT_CARD = 'credit_card', 'Carte Bancaire'
    CASH = 'cash', 'Espèces'


class PaymentStatus(models.TextChoices):
    """Statuts de paiement"""
    PENDING = 'pending', 'En attente'
    COMPLETED = 'completed', 'Complété'
    FAILED = 'failed', 'Échoué'
    REFUNDED = 'refunded', 'Remboursé'


class Location(models.Model):
    """Modèle pour les localisations (départ/arrivée)"""
    
    address = models.CharField(
        max_length=500,
        help_text="Adresse complète"
    )
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Latitude GPS"
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Longitude GPS"
    )
    
    landmark = models.CharField(
        max_length=200,
        blank=True,
        help_text="Point de repère (optionnel)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Localisation'
        verbose_name_plural = 'Localisations'
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.address}"


class Order(models.Model):
    """
    Modèle principal pour les commandes/trajets
    Enregistre chaque commande de transport
    """
    
    # Identificants
    reference = models.CharField(
        max_length=50,
        unique=True,
        help_text="Référence unique (auto-générée)"
    )
    
    # Utilisateurs
    user_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="ID du client qui a commandé"
    )
    
    driver_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text="ID du chauffeur assigné"
    )
    
    # Trajet
    pickup_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='pickups',
        help_text="Point de départ"
    )
    
    dropoff_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='dropoffs',
        help_text="Point d'arrivée"
    )
    
    estimated_distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Distance estimée en km"
    )
    
    actual_distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Distance réelle en km"
    )
    
    estimated_time = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Temps estimé en minutes"
    )
    
    actual_time = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Temps réel en minutes"
    )
    
    # Véhicule
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.TAXI
    )
    
    vehicle_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Plaque d'immatriculation"
    )
    
    # Options
    is_covoiturage = models.BooleanField(
        default=False,
        help_text="Client partage le trajet?"
    )
    
    is_bagages = models.BooleanField(
        default=False,
        help_text="Supplément bagages?"
    )
    
    # Tarification
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Tarif de base en XAF"
    )
    
    covoiturage_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Réduction covoiturage"
    )
    
    bagages_surcharge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Surcharge bagages"
    )
    
    promotion_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Réduction promotion appliquée"
    )
    
    tip_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Pourboire client"
    )
    
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Montant total en XAF"
    )
    
    # Paiement
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.MOVECOIN
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Montant payé"
    )
    
    # MOVECoin
    movecoin_earned = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="MOVECoin gagné par client"
    )
    
    driver_movecoin_earned = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="MOVECoin gagné par chauffeur"
    )
    
    # Statut
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True
    )
    
    # Commentaires
    user_notes = models.TextField(
        blank=True,
        help_text="Notes spéciales du client"
    )
    
    driver_notes = models.TextField(
        blank=True,
        help_text="Notes du chauffeur"
    )
    
    admin_notes = models.TextField(
        blank=True,
        help_text="Notes administrateur"
    )
    
    # Dates/Horaires
    scheduled_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Heure de commande planifiée"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    accepted_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    # Évaluations
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Note du client (1-5)"
    )
    
    user_review = models.TextField(
        blank=True,
        help_text="Avis du client"
    )
    
    driver_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Note du chauffeur (1-5)"
    )
    
    driver_review = models.TextField(
        blank=True,
        help_text="Avis du chauffeur"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['driver_id', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.reference} - {self.user_id} ({self.status})"
    
    def calculate_total_price(self):
        """Calculer le prix total"""
        total = self.base_price
        total -= self.covoiturage_discount
        total += self.bagages_surcharge
        total -= self.promotion_discount
        return max(total, 0)
    
    def can_cancel(self):
        """Vérifier si la commande peut être annulée"""
        cancellable_statuses = [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.ACCEPTED,
        ]
        return self.status in cancellable_statuses
    
    def is_completed(self):
        """La commande est-elle complétée?"""
        return self.status == OrderStatus.COMPLETED
    
    def calculate_movecoin(self):
        """Calculer le MOVECoin basé sur le montant payé"""
        # 1% du montant payé converti en MOVECoin
        return self.paid_amount * Decimal('0.01')
    
    def save(self, *args, **kwargs):
        """Générer la référence si elle n'existe pas"""
        if not self.reference:
            # Générer une référence: MOVE + date + ID
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.reference = f"MOVE-{timestamp}-{self.user_id[:4].upper()}"
        
        # Recalculer le total
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """Historique des changements de statut"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    
    from_status = models.CharField(max_length=20)
    to_status = models.CharField(max_length=20)
    
    changed_by = models.CharField(
        max_length=100,
        help_text="Qui a effectué le changement (user_id, driver_id, ou 'system')"
    )
    
    reason = models.TextField(
        blank=True,
        help_text="Raison du changement"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Historique Statut'
        verbose_name_plural = 'Historiques Statut'
        indexes = [
            models.Index(fields=['order', '-created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.order.reference}: {self.from_status} → {self.to_status}"


class OrderReview(models.Model):
    """Modèle pour les avis/évaluations"""
    
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='review'
    )
    
    # Avis client
    client_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    client_review = models.TextField(blank=True)
    client_reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Avis chauffeur
    driver_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    driver_review = models.TextField(blank=True)
    driver_reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
    
    def __str__(self):
        return f"Avis pour {self.order.reference}"
