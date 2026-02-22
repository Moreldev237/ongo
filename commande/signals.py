"""
Signaux Django pour l'app commande
Automatiser les actions lors de la création/modification de modèles
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderStatusHistory


@receiver(post_save, sender=Order)
def update_order_movecoin(sender, instance, created, **kwargs):
    """
    Calculer automatiquement le MOVECoin à la fin du trajet
    """
    if instance.status == 'completed' and not instance.movecoin_earned:
        instance.movecoin_earned = instance.calculate_movecoin()
        instance.save(update_fields=['movecoin_earned'])


@receiver(post_save, sender=Order)
def auto_confirm_order(sender, instance, created, **kwargs):
    """
    Confirmer automatiquement une commande après création
    """
    if created and instance.status == 'pending':
        # Auto-confirmer après création
        instance.status = 'confirmed'
        instance.confirmed_at = timezone.now()
        instance.save(update_fields=['status', 'confirmed_at'])
        
        # Créer l'enregistrement d'historique
        OrderStatusHistory.objects.create(
            order=instance,
            from_status='pending',
            to_status='confirmed',
            changed_by='system',
            reason='Auto-confirmation automatique'
        )
