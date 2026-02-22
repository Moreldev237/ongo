from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Promotion, UserPromotionUsage, PromotionType, PromoStatus


class PromotionModelTestCase(TestCase):
    """Tests pour le modèle Promotion"""
    
    def setUp(self):
        """Créer une promotion de test"""
        self.promotion = Promotion.objects.create(
            code='TEST25',
            name='Test Promo -25%',
            description='Une promotion de test',
            promo_type=PromotionType.COVOITURAGE,
            status=PromoStatus.ACTIVE,
            discount_type='percentage',
            discount_value=25.00,
            max_discount=5000.00,
            min_amount=1000.00,
            max_uses=1000,
            max_uses_per_user=5,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            created_by='admin'
        )
    
    def test_promotion_creation(self):
        """Tester la création d'une promotion"""
        self.assertEqual(self.promotion.code, 'TEST25')
        self.assertEqual(self.promotion.discount_value, 25.00)
        self.assertFalse(self.promotion.usage_count == 0)
    
    def test_promotion_is_valid(self):
        """Tester la validation d'une promotion"""
        self.assertTrue(self.promotion.is_valid())
    
    def test_promotion_expired(self):
        """Tester une promotion expirée"""
        expired_promo = Promotion.objects.create(
            code='EXPIRED',
            name='Promo Expirée',
            description='Expirée',
            status=PromoStatus.ACTIVE,
            discount_type='percentage',
            discount_value=10.00,
            start_date=timezone.now() - timedelta(days=2),
            end_date=timezone.now() - timedelta(days=1),
            created_by='admin'
        )
        self.assertFalse(expired_promo.is_valid())
    
    def test_calculate_discount_percentage(self):
        """Tester le calcul de réduction en pourcentage"""
        discount = self.promotion.calculate_discount(10000)
        expected = 2500.00  # 25% de 10000
        self.assertEqual(float(discount), expected)
    
    def test_calculate_discount_with_max(self):
        """Tester la réduction respectant le max_discount"""
        discount = self.promotion.calculate_discount(50000)
        # 25% de 50000 = 12500, mais max est 5000
        self.assertEqual(float(discount), 5000.00)
    
    def test_calculate_discount_below_minimum(self):
        """Tester avec montant en dessous du minimum"""
        discount = self.promotion.calculate_discount(500)
        self.assertEqual(float(discount), 0)
    
    def test_fixed_discount(self):
        """Tester une réduction fixe"""
        fixed_promo = Promotion.objects.create(
            code='FIXED100',
            name='Réduction Fixe 100 XAF',
            description='100 XAF fixes',
            status=PromoStatus.ACTIVE,
            discount_type='fixed',
            discount_value=100.00,
            min_amount=500.00,
            start_date=timezone.now(),
            created_by='admin'
        )
        discount = fixed_promo.calculate_discount(1000)
        self.assertEqual(float(discount), 100.00)


class PromotionAPITestCase(APITestCase):
    """Tests pour les endpoints API"""
    
    def setUp(self):
        """Initialiser les tests"""
        self.client = APIClient()
        
        # Créer une promotion active
        self.active_promo = Promotion.objects.create(
            code='COVOITURAGE',
            name='Covoiturage -25%',
            description='Partager le trajet = -25%',
            promo_type=PromotionType.COVOITURAGE,
            status=PromoStatus.ACTIVE,
            discount_type='percentage',
            discount_value=25.00,
            max_discount=5000.00,
            min_amount=1000.00,
            max_uses=10000,
            max_uses_per_user=5,
            applicable_to_covoiturage=True,
            applicable_to_bagages=False,
            cashback_percentage=2.50,
            priority=10,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            created_by='admin'
        )
    
    def test_list_active_promotions(self):
        """Tester la liste des promotions actives"""
        response = self.client.get('/api/promotions/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_apply_promotion_success(self):
        """Tester l'application réussie d'une promotion"""
        data = {
            'code': 'COVOITURAGE',
            'trip_amount': 10000,
            'user_id': 'user_123',
            'trip_id': 'trip_456',
            'covoiturage': True,
            'bagages': False
        }
        response = self.client.post('/api/promotions/apply/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(float(response.data['discount_amount']), 2500.00)
        self.assertEqual(float(response.data['final_amount']), 7500.00)
    
    def test_apply_promotion_invalid_code(self):
        """Tester l'application avec un code invalide"""
        data = {
            'code': 'INVALID',
            'trip_amount': 10000,
            'user_id': 'user_123'
        }
        response = self.client.post('/api/promotions/apply/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_apply_promotion_below_minimum(self):
        """Tester avec montant en dessous du minimum"""
        data = {
            'code': 'COVOITURAGE',
            'trip_amount': 500,  # < min_amount (1000)
            'user_id': 'user_123'
        }
        response = self.client.post('/api/promotions/apply/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_promotion_usage_tracking(self):
        """Tester le tracking des utilisations"""
        # Appliquer la promotion
        data = {
            'code': 'COVOITURAGE',
            'trip_amount': 5000,
            'user_id': 'user_123',
            'trip_id': 'trip_001'
        }
        response1 = self.client.post('/api/promotions/apply/', data, format='json')
        self.assertTrue(response1.data['success'])
        
        # Vérifier que l'utilisation a été enregistrée
        usage = UserPromotionUsage.objects.filter(
            user_id='user_123',
            promotion=self.active_promo
        )
        self.assertEqual(usage.count(), 1)
        self.assertEqual(float(usage[0].discount_applied), 1250.00)
    
    def test_promotion_max_uses_per_user(self):
        """Tester la limite d'utilisation par utilisateur"""
        # Utiliser la promotion 5 fois (max)
        for i in range(5):
            data = {
                'code': 'COVOITURAGE',
                'trip_amount': 5000,
                'user_id': 'user_123',
                'trip_id': f'trip_{i}'
            }
            response = self.client.post('/api/promotions/apply/', data, format='json')
            self.assertTrue(response.data['success'])
        
        # La 6ème tentative doit échouer
        data = {
            'code': 'COVOITURAGE',
            'trip_amount': 5000,
            'user_id': 'user_123',
            'trip_id': 'trip_extra'
        }
        response = self.client.post('/api/promotions/apply/', data, format='json')
        self.assertFalse(response.data['success'])
        self.assertIn('déjà utilisé', response.data['message'])
    
    def test_get_promotion_details(self):
        """Tester les détails d'une promotion"""
        response = self.client.get(f'/api/promotions/{self.active_promo.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'COVOITURAGE')
        self.assertTrue(response.data['is_valid'])
    
    def test_promotion_usage_history(self):
        """Tester l'historique d'utilisation"""
        # Appliquer une promotion
        data = {
            'code': 'COVOITURAGE',
            'trip_amount': 5000,
            'user_id': 'user_test'
        }
        self.client.post('/api/promotions/apply/', data, format='json')
        
        # Vérifie l'historique
        response = self.client.get('/api/promotion-usages/?user_id=user_test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)


class PromotionEdgeCasesTestCase(TestCase):
    """Tests des cas limites"""
    
    def setUp(self):
        """Initialiser les tests"""
        self.promotion = Promotion.objects.create(
            code='EDGE',
            name='Test Edge Cases',
            status=PromoStatus.ACTIVE,
            discount_type='percentage',
            discount_value=10.00,
            max_uses=2,  # Très limité
            max_uses_per_user=1,
            start_date=timezone.now(),
            created_by='admin'
        )
    
    def test_promotion_max_uses_global(self):
        """Tester la limite d'utilisation globale"""
        # Utiliser la promo 2 fois (max global)
        for i in range(2):
            UserPromotionUsage.objects.create(
                user_id=f'user_{i}',
                promotion=self.promotion,
                discount_applied=100,
                trip_amount=1000
            )
            self.promotion.usage_count += 1
        self.promotion.save()
        
        # Vérifier que is_valid retourne False
        self.assertFalse(self.promotion.is_valid())
    
    def test_zero_discount(self):
        """Tester une réduction de 0%"""
        no_discount = Promotion.objects.create(
            code='NODISCOUNT',
            name='Pas de Promo',
            status=PromoStatus.ACTIVE,
            discount_type='percentage',
            discount_value=0,
            start_date=timezone.now(),
            created_by='admin'
        )
        discount = no_discount.calculate_discount(5000)
        self.assertEqual(float(discount), 0)

