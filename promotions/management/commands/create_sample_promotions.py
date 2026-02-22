from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from promotions.models import Promotion, PromotionType, PromoStatus


class Command(BaseCommand):
    help = 'Créer des promotions de test pour le développement'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Nombre de promotions à créer'
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Supprimer toutes les promotions de test avant de créer'
        )
    
    def handle(self, *args, **options):
        if options['delete']:
            count = Promotion.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'✓ {count} promotions supprimées'))
        
        # Promotions de base
        promotions_data = [
            {
                'code': 'COVOITURAGE',
                'name': 'Covoiturage -25%',
                'description': 'Obtenez 25% de réduction en partageant votre trajet avec d\'autres passagers',
                'promo_type': PromotionType.COVOITURAGE,
                'discount_value': 25.00,
                'applicable_to_covoiturage': True,
                'applicable_to_bagages': False,
                'max_uses': 50000,
                'cashback_percentage': 2.50,
                'priority': 10,
            },
            {
                'code': 'BAGAGES',
                'name': 'Bagages -10%',
                'description': 'Réduction de 10% sur le supplément bagages',
                'promo_type': PromotionType.BAGAGES,
                'discount_value': 10.00,
                'applicable_to_covoiturage': False,
                'applicable_to_bagages': True,
                'max_uses': 30000,
                'cashback_percentage': 1.50,
                'priority': 8,
            },
            {
                'code': 'FIRST5K',
                'name': 'Premier trajet -20%',
                'description': 'Réduction de 20% pour votre premiere réservation',
                'promo_type': PromotionType.FIRST_TIME,
                'discount_type': 'percentage',
                'discount_value': 20.00,
                'max_uses_per_user': 1,
                'max_uses': 5000,
                'target_users': 'new',
                'cashback_percentage': 3.00,
                'priority': 15,
            },
            {
                'code': 'MOVECOIN20',
                'name': 'MOVECoin 20% Cashback',
                'description': 'Gagnez 20% de réduction en MOVECoin sur tous les trajets',
                'promo_type': PromotionType.CASHBACK,
                'discount_type': 'percentage',
                'discount_value': 5.00,
                'max_discount': 1000.00,
                'cashback_percentage': 20.00,
                'max_uses': 100000,
                'priority': 5,
            },
            {
                'code': 'LOYAL10',
                'name': 'Client Fidèle -10%',
                'description': 'Remerciement des clients fidèles',
                'promo_type': PromotionType.LOYAL_CLIENT,
                'discount_value': 10.00,
                'target_users': 'loyal',
                'max_uses': 20000,
                'cashback_percentage': 1.00,
                'priority': 7,
            },
            {
                'code': 'REFERRAL500',
                'name': 'Parrainage (500 XAF)',
                'description': 'Promouvez MOVENOW et recevez 500 XAF de bonus',
                'promo_type': PromotionType.REFERRAL,
                'discount_type': 'fixed',
                'discount_value': 500.00,
                'min_amount': 0,
                'max_uses': 10000,
                'max_uses_per_user': 10,
                'cashback_percentage': 0,
                'priority': 12,
            },
            {
                'code': 'WEEKEND15',
                'name': 'Week-end -15%',
                'description': 'Réduction spéciale les week-ends (samedi et dimanche)',
                'promo_type': PromotionType.SEASONAL,
                'discount_value': 15.00,
                'max_uses': 40000,
                'cashback_percentage': 2.00,
                'priority': 9,
            },
            {
                'code': 'MONTHEND',
                'name': 'Fin du mois -30%',
                'description': 'Grosse réduction en fin de mois',
                'promo_type': PromotionType.SEASONAL,
                'discount_value': 30.00,
                'max_discount': 3000.00,
                'max_uses': 5000,
                'cashback_percentage': 5.00,
                'priority': 20,
                'end_date': timezone.now() + timedelta(days=7),
            },
            {
                'code': 'VIP50',
                'name': 'Utilisateur VIP -50%',
                'description': 'Accés VIP avec réductions majeures',
                'promo_type': PromotionType.LOYAL_CLIENT,
                'discount_value': 50.00,
                'max_discount': 10000.00,
                'target_users': 'vip',
                'max_uses': 2000,
                'max_uses_per_user': 100,
                'cashback_percentage': 10.00,
                'priority': 25,
            },
            {
                'code': 'MARCHPROM',
                'name': 'Promotion Mars 2026',
                'description': 'Promotion limitée pour le mois de mars',
                'promo_type': PromotionType.SEASONAL,
                'discount_value': 18.00,
                'max_uses': 8000,
                'cashback_percentage': 3.50,
                'priority': 6,
                'start_date': timezone.now() + timedelta(days=5),
                'end_date': timezone.now() + timedelta(days=35),
            },
        ]
        
        created = 0
        for promo_data in promotions_data[:options['count']]:
            # Définir les dates par défaut
            if 'start_date' not in promo_data:
                promo_data['start_date'] = timezone.now()
            if 'end_date' not in promo_data:
                promo_data['end_date'] = timezone.now() + timedelta(days=365)
            
            # Définir les autres champs par défaut
            promo_data.setdefault('status', PromoStatus.ACTIVE)
            promo_data.setdefault('discount_type', 'percentage')
            promo_data.setdefault('min_amount', 1000.00)
            promo_data.setdefault('max_uses_per_user', 5)
            promo_data.setdefault('applicable_to_covoiturage', True)
            promo_data.setdefault('applicable_to_bagages', True)
            promo_data.setdefault('target_users', 'all')
            promo_data.setdefault('created_by', 'system')
            
            Promotion.objects.get_or_create(
                code=promo_data['code'],
                defaults=promo_data
            )
            created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ {created} promotions de test créées avec succès!')
        )
