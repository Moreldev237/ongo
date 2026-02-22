from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

class PromotionType(models.TextChoices):
    """Types de promotions disponibles"""
    COVOITURAGE = 'covoiturage', 'Covoiturage (-25%)'
    BAGAGES = 'bagages', 'Bagages (-10%)'
    LOYAL_CLIENT = 'loyal_client', 'Client Fidèle'
    REFERRAL = 'referral', 'Parrainage'
    SEASONAL = 'seasonal', 'Saisonnière'
    FIRST_TIME = 'first_time', 'Premier Trajet'
    CASHBACK = 'cashback', 'Cashback MOVECoin'


class PromoStatus(models.TextChoices):
    """Statut des promotions"""
    DRAFT = 'draft', 'Brouillon'
    ACTIVE = 'active', 'Actif'
    PAUSED = 'paused', 'Suspendu'
    EXPIRED = 'expired', 'Expiré'
    ARCHIVED = 'archived', 'Archivé'


class Promotion(models.Model):
    """
    Modèle principal pour gérer les promotions
    """
    code = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="Code promotionnel unique (ex: MOVE25, COVOITURAGE)"
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Nom lisible de la promotion (ex: Covoiturage -25%)"
    )
    
    description = models.TextField(
        help_text="Description détaillée de la promotion"
    )
    
    promo_type = models.CharField(
        max_length=20,
        choices=PromotionType.choices,
        default=PromotionType.SEASONAL
    )
    
    status = models.CharField(
        max_length=20,
        choices=PromoStatus.choices,
        default=PromoStatus.DRAFT
    )
    
    # Réduction
    discount_type = models.CharField(
        max_length=20,
        choices=[('percentage', 'Pourcentage'), ('fixed', 'Montant fixe')],
        default='percentage',
        help_text="Type de réduction: pourcentage ou montant fixe"
    )
    
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Valeur de la réduction (% ou montant)"
    )
    
    max_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Réduction maximale en MOVECoin (optionnel)"
    )
    
    min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Montant minimum pour appliquer la promo"
    )
    
    # Validité temporelle
    start_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date de début de la promotion"
    )
    
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de fin de la promotion (null = sans limite)"
    )
    
    # Limitations d'utilisation
    max_uses = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Nombre maximum d'utilisations (null = illimité)"
    )
    
    max_uses_per_user = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Nombre maximum d'utilisations par utilisateur"
    )
    
    usage_count = models.IntegerField(
        default=0,
        help_text="Nombre d'utilisations actuelles"
    )
    
    # Ciblage
    target_users = models.CharField(
        max_length=50,
        choices=[
            ('all', 'Tous les utilisateurs'),
            ('new', 'Nouveaux utilisateurs'),
            ('loyal', 'Clients fidèles'),
            ('vip', 'Utilisateurs VIP'),
        ],
        default='all'
    )
    
    # Conditions
    applicable_to_covoiturage = models.BooleanField(
        default=True,
        help_text="La promo s'applique-t-elle au covoiturage?"
    )
    
    applicable_to_bagages = models.BooleanField(
        default=True,
        help_text="La promo s'applique-t-elle aux bagages?"
    )
    
    # MOVECoin
    cashback_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pourcentage de MOVECoin retourné (0-100%)"
    )
    
    # Métadonnées
    priority = models.IntegerField(
        default=0,
        help_text="Priorité d'affichage (plus élevé = plus important)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, help_text="Admin qui a créé cette promo")
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'
        indexes = [
            models.Index(fields=['code', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.status})"
    
    def is_valid(self):
        """Vérifier si la promotion est valide"""
        now = timezone.now()
        
        # Vérifier le statut
        if self.status != PromoStatus.ACTIVE:
            return False
        
        # Vérifier la date de début
        if self.start_date > now:
            return False
        
        # Vérifier la date de fin
        if self.end_date and self.end_date < now:
            return False
        
        # Vérifier le max d'utilisations
        if self.max_uses and self.usage_count >= self.max_uses:
            return False
        
        return True
    
    def calculate_discount(self, amount):
        """Calculer le montant de réduction"""
        if not self.is_valid():
            return 0
        
        if amount < self.min_amount:
            return 0
        
        if self.discount_type == 'percentage':
            discount = (amount * self.discount_value) / 100
        else:
            discount = self.discount_value
        
        # Appliquer le maximum de réduction
        if self.max_discount:
            discount = min(discount, self.max_discount)
        
        return discount


class UserPromotionUsage(models.Model):
    """
    Historique d'utilisation des promotions par utilisateur
    """
    user_id = models.CharField(max_length=100)  # ID utilisateur flexible
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name='usages'
    )
    
    used_at = models.DateTimeField(auto_now_add=True)
    discount_applied = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    trip_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    trip_id = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        ordering = ['-used_at']
        verbose_name = 'Utilisation Promotion'
        verbose_name_plural = 'Utilisations Promotions'
        indexes = [
            models.Index(fields=['user_id', 'used_at']),
            models.Index(fields=['promotion', 'used_at']),
        ]
    
    def __str__(self):
        return f"{self.user_id} - {self.promotion.code} ({self.used_at.date()})"
