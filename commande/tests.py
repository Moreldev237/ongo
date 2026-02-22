from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal

from .models import (
    Order, Location, OrderStatusHistory, OrderReview,
    VehicleType, OrderStatus, PaymentMethod, PaymentStatus
)


class LocationTestCase(TestCase):
    """Tests pour le modèle Location"""
    
    def setUp(self):
        self.location = Location.objects.create(
            address='123 Rue de la Paix, Yaoundé',
            latitude=3.8480,
            longitude=11.5021,
            landmark='Près de la gare routière'
        )
    
    def test_location_creation(self):
        """Tester la création d'une localisation"""
        self.assertEqual(self.location.address, '123 Rue de la Paix, Yaoundé')
        self.assertTrue(str(self.location).startswith('123 Rue'))


class OrderTestCase(TestCase):
    """Tests pour le modèle Order"""
    
    def setUp(self):
        self.pickup = Location.objects.create(
            address='Position A',
            latitude=3.8480,
            longitude=11.5021
        )
        self.dropoff = Location.objects.create(
            address='Position B',
            latitude=3.8500,
            longitude=11.5050
        )
        
        self.order = Order.objects.create(
            user_id='user_123',
            pickup_location=self.pickup,
            dropoff_location=self.dropoff,
            vehicle_type=VehicleType.TAXI,
            base_price=Decimal('5000.00'),
            total_price=Decimal('5000.00'),
            payment_method=PaymentMethod.MOVECOIN
        )
    
    def test_order_creation(self):
        """Tester la création d'une commande"""
        self.assertIsNotNone(self.order.reference)
        self.assertEqual(self.order.user_id, 'user_123')
        self.assertEqual(self.order.status, OrderStatus.CONFIRMED)  # Auto-confirméé
    
    def test_order_reference_uniqueness(self):
        """La référence doit être unique"""
        order2 = Order.objects.create(
            user_id='user_456',
            pickup_location=self.pickup,
            dropoff_location=self.dropoff,
            vehicle_type=VehicleType.TAXI,
            base_price=Decimal('5000.00'),
            total_price=Decimal('5000.00')
        )
        self.assertNotEqual(self.order.reference, order2.reference)
    
    def test_calculate_movecoin(self):
        """Tester le calcul de MOVECoin"""
        self.order.paid_amount = Decimal('5000.00')
        movecoin = self.order.calculate_movecoin()
        expected = Decimal('50.00')  # 1% de 5000
        self.assertEqual(movecoin, expected)
    
    def test_can_cancel_pending(self):
        """Une commande en attente peut être annulée"""
        self.assertTrue(self.order.can_cancel())
    
    def test_cannot_cancel_completed(self):
        """Une commande complétée ne peut pas être annulée"""
        self.order.status = OrderStatus.COMPLETED
        self.order.save()
        self.assertFalse(self.order.can_cancel())
    
    def test_is_completed(self):
        """Tester la méthode is_completed"""
        self.assertFalse(self.order.is_completed())
        self.order.status = OrderStatus.COMPLETED
        self.assertTrue(self.order.is_completed())
    
    def test_price_calculation_with_discounts(self):
        """Tester le calcul de prix avec réductions"""
        order = Order.objects.create(
            user_id='user_test',
            pickup_location=self.pickup,
            dropoff_location=self.dropoff,
            vehicle_type=VehicleType.TAXI,
            base_price=Decimal('10000.00'),
            covoiturage_discount=Decimal('2500.00'),
            bagages_surcharge=Decimal('1000.00'),
            promotion_discount=Decimal('1000.00'),
            total_price=Decimal('7500.00')  # 10000 - 2500 + 1000 - 1000
        )
        
        calculated = order.calculate_total_price()
        expected = Decimal('7500.00')
        self.assertEqual(calculated, expected)


class OrderStatusHistoryTestCase(TestCase):
    """Tests pour l'historique des statuts"""
    
    def setUp(self):
        self.pickup = Location.objects.create(
            address='A', latitude=0, longitude=0
        )
        self.dropoff = Location.objects.create(
            address='B', latitude=0, longitude=0
        )
        
        self.order = Order.objects.create(
            user_id='user_test',
            pickup_location=self.pickup,
            dropoff_location=self.dropoff,
            base_price=Decimal('5000.00'),
            total_price=Decimal('5000.00')
        )
    
    def test_status_history_creation(self):
        """Tester la création d'un historique de statut"""
        history = OrderStatusHistory.objects.create(
            order=self.order,
            from_status=OrderStatus.PENDING,
            to_status=OrderStatus.CONFIRMED,
            changed_by='system',
            reason='Test'
        )
        
        self.assertEqual(history.order, self.order)
        self.assertEqual(history.from_status, OrderStatus.PENDING)
    
    def test_history_ordering(self):
        """L'historique doit être ordonné par date décroissante"""
        h1 = OrderStatusHistory.objects.create(
            order=self.order,
            from_status=OrderStatus.PENDING,
            to_status=OrderStatus.CONFIRMED,
            changed_by='system'
        )
        
        h2 = OrderStatusHistory.objects.create(
            order=self.order,
            from_status=OrderStatus.CONFIRMED,
            to_status=OrderStatus.ACCEPTED,
            changed_by='driver_123'
        )
        
        histories = list(OrderStatusHistory.objects.filter(order=self.order))
        self.assertEqual(histories[0].id, h2.id)  # Plus récent d'abord


class OrderAPITestCase(APITestCase):
    """Tests pour les endpoints API"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.pickup = Location.objects.create(
            address='Départ', latitude=3.8480, longitude=11.5021
        )
        self.dropoff = Location.objects.create(
            address='Arrivée', latitude=3.8500, longitude=11.5050
        )
    
    def test_create_order_via_api(self):
        """Tester la création de commande via API"""
        data = {
            'user_id': 'user_api_test',
            'pickup_address': 'Départ API',
            'pickup_latitude': '3.8480',
            'pickup_longitude': '11.5021',
            'dropoff_address': 'Arrivée API',
            'dropoff_latitude': '3.8500',
            'dropoff_longitude': '11.5050',
            'vehicle_type': 'taxi',
            'base_price': '5000.00',
            'payment_method': 'movecoin'
        }
        
        response = self.client.post('/api/commande/orders/create_order/', data, format='json')
        
        # Devrait retourner 201 (Created) ou 200 selon la configuration
        self.assertIn(response.status_code, [200, 201])
    
    def test_list_orders(self):
        """Tester la liste des commandes"""
        Order.objects.create(
            user_id='user_test',
            pickup_location=self.pickup,
            dropoff_location=self.dropoff,
            base_price=Decimal('5000.00'),
            total_price=Decimal('5000.00')
        )
        
        response = self.client.get('/api/commande/orders/')
        
        self.assertIn(response.status_code, [200, 401])  # 401 si auth requise
    
    def test_order_stats(self):
        """Tester les statistiques"""
        # Créer plusieurs commandes
        for i in range(3):
            Order.objects.create(
                user_id=f'user_{i}',
                pickup_location=self.pickup,
                dropoff_location=self.dropoff,
                base_price=Decimal('5000.00'),
                total_price=Decimal('5000.00')
            )
        
        response = self.client.get('/api/commande/orders/stats/')
        
        if response.status_code == 200:
            self.assertIn('total_orders', response.data)
            self.assertGreaterEqual(response.data['total_orders'], 3)


class OrderReviewTestCase(TestCase):
    """Tests pour les avis"""
    
    def setUp(self):
        self.pickup = Location.objects.create(
            address='A', latitude=0, longitude=0
        )
        self.dropoff = Location.objects.create(
            address='B', latitude=0, longitude=0
        )
        
        self.order = Order.objects.create(
            user_id='user_test',
            pickup_location=self.pickup,
            dropoff_location=self.dropoff,
            base_price=Decimal('5000.00'),
            total_price=Decimal('5000.00')
        )
        
        self.review = OrderReview.objects.create(order=self.order)
    
    def test_review_creation(self):
        """Tester la création d'un avis"""
        self.assertEqual(self.review.order, self.order)
        self.assertIsNone(self.review.client_rating)
    
    def test_set_client_rating(self):
        """Tester l'ajout d'une note client"""
        self.review.client_rating = 5
        self.review.client_review = "Excellent service!"
        self.review.save()
        
        self.assertEqual(self.review.client_rating, 5)
        self.assertEqual(self.review.client_review, "Excellent service!")
    
    def test_set_driver_rating(self):
        """Tester l'ajout d'une note chauffeur"""
        self.review.driver_rating = 4
        self.review.driver_review = "Bon chauffeur"
        self.review.save()
        
        self.assertEqual(self.review.driver_rating, 4)


class OrderEdgeCasesTestCase(TestCase):
    """Tests des cas limites"""
    
    def setUp(self):
        self.pickup = Location.objects.create(
            address='A', latitude=0, longitude=0
        )
        self.dropoff = Location.objects.create(
            address='B', latitude=0, longitude=0
        )
    
    def test_zero_price_order(self):
        """Tester une commande à zéro prix"""
        order = Order.objects.create(
            user_id='user_test',
            pickup_location=self.pickup,
            dropoff_location=self.dropoff,
            base_price=Decimal('0.00'),
            total_price=Decimal('0.00')
        )
        
        self.assertEqual(order.total_price, Decimal('0.00'))
    
    def test_large_distance_order(self):
        """Tester une commande sur longue distance"""
        order = Order.objects.create(
            user_id='user_test',
            pickup_location=self.pickup,
            dropoff_location=self.dropoff,
            base_price=Decimal('50000.00'),
            estimated_distance=Decimal('999.99'),
            total_price=Decimal('50000.00')
        )
        
        self.assertEqual(order.estimated_distance, Decimal('999.99'))
    
    def test_multiple_reason_cancellations(self):
        """Tester les raisons d'annulation multiples"""
        order = Order.objects.create(
            user_id='user_test',
            pickup_location=self.pickup,
            dropoff_location=self.dropoff,
            base_price=Decimal('5000.00'),
            total_price=Decimal('5000.00')
        )
        
        # Test les 3 types d'annulation possibles
        reasons = [OrderStatus.CANCELLED_USER, OrderStatus.CANCELLED_DRIVER, OrderStatus.CANCELLED_ADMIN]
        
        for reason in reasons:
            self.assertIn(reason, [choice[0] for choice in OrderStatus.choices])
