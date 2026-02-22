from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q, Sum, Avg, Count
from decimal import Decimal

from .models import (
    Order, Location, OrderStatusHistory, OrderReview,
    VehicleType, OrderStatus, PaymentMethod, PaymentStatus
)
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    LocationSerializer,
    OrderStatusHistorySerializer,
    CreateOrderSerializer,
    UpdateOrderStatusSerializer,
    RateOrderSerializer,
    OrderStatsSerializer,
)


class LocationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les localisations"""
    
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Chercher des localisations à proximité"""
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        radius = request.data.get('radius', 5)  # 5 km par défaut
        
        if not latitude or not longitude:
            return Response(
                {'error': 'latitude et longitude requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Requête simple (à améliorer avec math distance réelle)
        locations = Location.objects.filter(
            latitude__range=[float(latitude) - radius / 111, float(latitude) + radius / 111],
            longitude__range=[float(longitude) - radius / 111, float(longitude) + radius / 111]
        )
        
        serializer = self.get_serializer(locations, many=True)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les commandes
    GET /api/commande/orders/ - Lister
    POST /api/commande/orders/ - Créer
    GET /api/commande/orders/{id}/ - Détails
    PATCH /api/commande/orders/{id}/ - Modifier
    DELETE /api/commande/orders/{id}/ - Annuler
    POST /api/commande/orders/accept/ - Accepter la commande
    POST /api/commande/orders/start/ - Démarrer le trajet
    POST /api/commande/orders/complete/ - Terminer
    POST /api/commande/orders/cancel/ - Annuler
    POST /api/commande/orders/rate/ - Évaluer
    GET /api/commande/orders/stats/ - Statistiques
    GET /api/commande/orders/history/ - Historique utilisateur
    """
    
    queryset = Order.objects.all()
    
    def get_permissions(self):
        """Permissions selon l'action"""
        if self.action in ['stats', 'list']:
            return [AllowAny()]  # Allow unauthenticated access to stats and list for frontend
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Choisir le serializer selon l'action"""
        if self.action == 'retrieve':
            return OrderDetailSerializer
        elif self.action == 'create':
            return CreateOrderSerializer
        elif self.action == 'list':
            return OrderListSerializer
        elif self.action in ['update_status', 'accept', 'start', 'complete', 'cancel']:
            return UpdateOrderStatusSerializer
        elif self.action == 'rate':
            return RateOrderSerializer
        elif self.action == 'stats':
            return OrderStatsSerializer
        return OrderDetailSerializer
    
    def get_queryset(self):
        """Filtrer selon les permissions"""
        user_id = getattr(self.request.user, 'id', None)
        
        # Les utilisateurs voient uniquement leurs propres commandes
        if not self.request.user.is_staff:
            return Order.objects.filter(user_id=user_id)
        
        # Les admins voient tout
        return Order.objects.all()
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """
        Créer une nouvelle commande
        POST /api/commande/orders/create_order/
        """
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Récupérer ou créer les localisations
            if serializer.validated_data.get('pickup_location_id'):
                pickup_location = Location.objects.get(id=serializer.validated_data['pickup_location_id'])
            else:
                pickup_location, _ = Location.objects.get_or_create(
                    address=serializer.validated_data['pickup_address'],
                    latitude=serializer.validated_data['pickup_latitude'],
                    longitude=serializer.validated_data['pickup_longitude'],
                    defaults={'landmark': serializer.validated_data.get('pickup_landmark', '')}
                )
            
            if serializer.validated_data.get('dropoff_location_id'):
                dropoff_location = Location.objects.get(id=serializer.validated_data['dropoff_location_id'])
            else:
                dropoff_location, _ = Location.objects.get_or_create(
                    address=serializer.validated_data['dropoff_address'],
                    latitude=serializer.validated_data['dropoff_latitude'],
                    longitude=serializer.validated_data['dropoff_longitude'],
                    defaults={'landmark': serializer.validated_data.get('dropoff_landmark', '')}
                )
            
            # Créer la commande
            order = Order.objects.create(
                user_id=serializer.validated_data['user_id'],
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                vehicle_type=serializer.validated_data['vehicle_type'],
                estimated_distance=serializer.validated_data.get('estimated_distance'),
                estimated_time=serializer.validated_data.get('estimated_time'),
                is_covoiturage=serializer.validated_data['is_covoiturage'],
                is_bagages=serializer.validated_data['is_bagages'],
                base_price=serializer.validated_data['base_price'],
                payment_method=serializer.validated_data['payment_method'],
                scheduled_time=serializer.validated_data.get('scheduled_time'),
                user_notes=serializer.validated_data.get('user_notes', ''),
                status=OrderStatus.PENDING,
                total_price=serializer.validated_data['base_price'],
            )
            
            # Enregistrer le changement de statut initial
            OrderStatusHistory.objects.create(
                order=order,
                from_status='',
                to_status=OrderStatus.PENDING,
                changed_by=serializer.validated_data['user_id'],
                reason='Création de la commande'
            )
            
            # Créer l'avis (vide au départ)
            OrderReview.objects.create(order=order)
            
            result_serializer = OrderDetailSerializer(order)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Mettre à jour le statut d'une commande"""
        order = self.get_object()
        serializer = UpdateOrderStatusSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = order.status
        new_status = serializer.validated_data['new_status']
        
        # Mettre à jour le statut
        order.status = new_status
        
        # Mettre à jour les timestamps
        if new_status == OrderStatus.CONFIRMED:
            order.confirmed_at = timezone.now()
        elif new_status == OrderStatus.ACCEPTED:
            order.accepted_at = timezone.now()
        elif new_status == OrderStatus.IN_PROGRESS:
            order.started_at = timezone.now()
        elif new_status == OrderStatus.COMPLETED:
            order.completed_at = timezone.now()
            # Calculer MOVECoin
            order.movecoin_earned = order.calculate_movecoin()
        elif new_status in [OrderStatus.CANCELLED_USER, OrderStatus.CANCELLED_DRIVER, OrderStatus.CANCELLED_ADMIN]:
            order.cancelled_at = timezone.now()
        
        order.save()
        
        # Enregistrer l'historique
        OrderStatusHistory.objects.create(
            order=order,
            from_status=old_status,
            to_status=new_status,
            changed_by=serializer.validated_data['changed_by'],
            reason=serializer.validated_data.get('reason', '')
        )
        
        result_serializer = OrderDetailSerializer(order)
        return Response(result_serializer.data)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accepter la commande (chauffeur)"""
        order = self.get_object()
        
        if order.status != OrderStatus.CONFIRMED:
            return Response(
                {'error': 'La commande doit être confirmée avant acceptation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = OrderStatus.ACCEPTED
        order.driver_id = request.data.get('driver_id')
        order.accepted_at = timezone.now()
        order.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            from_status=OrderStatus.CONFIRMED,
            to_status=OrderStatus.ACCEPTED,
            changed_by=order.driver_id,
            reason='Chauffeur accepte la course'
        )
        
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Démarrer le trajet"""
        order = self.get_object()
        
        if order.status != OrderStatus.DRIVER_ARRIVED:
            return Response(
                {'error': 'Le chauffeur doit être arrivé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = OrderStatus.IN_PROGRESS
        order.started_at = timezone.now()
        order.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            from_status=OrderStatus.DRIVER_ARRIVED,
            to_status=OrderStatus.IN_PROGRESS,
            changed_by=order.driver_id,
            reason='Trajet commence'
        )
        
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Terminer la commande"""
        order = self.get_object()
        
        if order.status not in [OrderStatus.IN_PROGRESS, OrderStatus.DRIVER_ARRIVED]:
            return Response(
                {'error': 'La commande n\'est pas en cours'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour les informations finales
        order.status = OrderStatus.COMPLETED
        order.completed_at = timezone.now()
        order.actual_distance = request.data.get('actual_distance', order.estimated_distance)
        order.actual_time = request.data.get('actual_time', order.estimated_time)
        order.paid_amount = order.total_price + request.data.get('tip_amount', 0)
        order.tip_amount = request.data.get('tip_amount', 0)
        order.payment_status = PaymentStatus.COMPLETED
        order.movecoin_earned = order.calculate_movecoin()
        order.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            from_status=OrderStatus.IN_PROGRESS,
            to_status=OrderStatus.COMPLETED,
            changed_by=order.driver_id,
            reason='Trajet complété'
        )
        
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler la commande"""
        order = self.get_object()
        
        if not order.can_cancel():
            return Response(
                {'error': f'Impossible d\'annuler une commande au statut {order.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cancelled_by = request.data.get('cancelled_by', 'unknown')
        
        if cancelled_by == 'user':
            order.status = OrderStatus.CANCELLED_USER
        elif cancelled_by == 'driver':
            order.status = OrderStatus.CANCELLED_DRIVER
        else:
            order.status = OrderStatus.CANCELLED_ADMIN
        
        order.cancelled_at = timezone.now()
        order.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            from_status=request.data.get('previous_status', ''),
            to_status=order.status,
            changed_by=cancelled_by,
            reason=request.data.get('reason', 'Annulation')
        )
        
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Évaluer la commande"""
        order = self.get_object()
        serializer = RateOrderSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        review, _ = OrderReview.objects.get_or_create(order=order)
        
        reviewer_type = serializer.validated_data['reviewer_type']
        rating = serializer.validated_data['rating']
        review_text = serializer.validated_data.get('review', '')
        
        if reviewer_type == 'client':
            review.client_rating = rating
            review.client_review = review_text
            review.client_reviewed_at = timezone.now()
            order.user_rating = rating
            order.user_review = review_text
        else:
            review.driver_rating = rating
            review.driver_review = review_text
            review.driver_reviewed_at = timezone.now()
            order.driver_rating = rating
            order.driver_review = review_text
        
        review.save()
        order.save()
        
        result_serializer = OrderDetailSerializer(order)
        return Response(result_serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Récupérer les statistiques des commandes"""
        queryset = self.get_queryset()
        
        # Si filtre par utilisateur
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Si filtre par driver
        driver_id = request.query_params.get('driver_id')
        if driver_id:
            queryset = queryset.filter(driver_id=driver_id)
        
        stats = {
            'total_orders': queryset.count(),
            'completed_orders': queryset.filter(status=OrderStatus.COMPLETED).count(),
            'cancelled_orders': queryset.filter(
                status__in=[OrderStatus.CANCELLED_USER, OrderStatus.CANCELLED_DRIVER, OrderStatus.CANCELLED_ADMIN]
            ).count(),
            'pending_orders': queryset.filter(status=OrderStatus.PENDING).count(),
            'total_revenue': queryset.aggregate(Sum('total_price'))['total_price__sum'] or 0,
            'average_rating': queryset.aggregate(Avg('user_rating'))['user_rating__avg'] or 0,
            'total_distance': queryset.aggregate(Sum('actual_distance'))['actual_distance__sum'] or 0,
            'total_time': queryset.aggregate(Sum('actual_time'))['actual_time__sum'] or 0,
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Récupérer l'historique des commandes d'un utilisateur"""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id paramètre requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orders = Order.objects.filter(user_id=user_id).order_by('-created_at')
        
        # Pagination simple
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))
        
        total = orders.count()
        orders = orders[offset:offset + limit]
        
        serializer = OrderListSerializer(orders, many=True)
        return Response({
            'count': total,
            'results': serializer.data
        })
