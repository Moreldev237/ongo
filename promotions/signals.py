"""
Signaux Django pour l'app promotions
Automatiser les actions lors de la création/modification de modèles
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Promotion, UserPromotionUsage


@receiver(post_save, sender=UserPromotionUsage)
def update_promotion_usage_count(sender, instance, created, **kwargs):
    """
    Mise à jour automatique du compteur d'utilisation de la promotion
    Appelé après la création d'une utilisation
    """
    if created:
        promotion = instance.promotion
        promotion.usage_count += 1
        promotion.save(update_fields=['usage_count'])


@receiver(post_delete, sender=UserPromotionUsage)
def decrease_promotion_usage_count(sender, instance, **kwargs):
    """
    Diminuer le compteur si une utilisation est supprimée
    """
    promotion = instance.promotion
    if promotion.usage_count > 0:
        promotion.usage_count -= 1
        promotion.save(update_fields=['usage_count'])


@receiver(post_save, sender=Promotion)
def check_promotion_expiry(sender, instance, **kwargs):
    """
    Vérifier et mettre à jour le statut des promotions expirées
    """
    if instance.status == 'active':
        now = timezone.now()
        
        # Vérifier si expirée
        if instance.end_date and instance.end_date < now:
            instance.status = 'expired'
            # Utiliser update() pour éviter les boucles infinies de signaux
            Promotion.objects.filter(pk=instance.pk).update(status='expired')
        
        # Vérifier si le max d'utilisation est atteint
        if instance.max_uses and instance.usage_count >= instance.max_uses:
            instance.status = 'expired'
            Promotion.objects.filter(pk=instance.pk).update(status='expired')
