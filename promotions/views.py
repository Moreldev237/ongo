from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils import timezone
from django.db.models import Q, F, Count
from decimal import Decimal

from .models import Promotion, UserPromotionUsage, PromoStatus
from .serializers import (
    PromotionSerializer,
    PromotionDetailSerializer,
    PromotionListSerializer,
    UserPromotionUsageSerializer,
    ApplyPromotionSerializer,
    PromotionResponseSerializer,
    CreatePromotionSerializer,
)


class PromotionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les promotions
    - GET /promotions/ : Lister les promotions actives
    - GET /promotions/{id}/ : Détails d'une promotion
    - POST /promotions/ : Créer une promotion (admin)
    - PUT /promotions/{id}/ : Modifier une promotion (admin)
    - PATCH /promotions/{id}/ : Modifier partiellement (admin)
    - DELETE /promotions/{id}/ : Supprimer (admin)
    - POST /promotions/apply/ : Appliquer une promotion
    - GET /promotions/active/ : Lister les promos actives
    - GET /promotions/stats/ : Statistiques (admin)
    """
    
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    
    def get_permissions(self):
        """Permissions selon l'action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'stats']:
            return [IsAdminUser()]
        elif self.action in ['apply']:
            return [IsAuthenticated()]
        else:  # list, active, retrieve
            return [AllowAny()]  # Allow anonymous access to view promotions
    
    def get_serializer_class(self):
        """Choisir le serializer selon l'action"""
        if self.action == 'retrieve':
            return PromotionDetailSerializer
        elif self.action == 'list':
            return PromotionListSerializer
        elif self.action == 'create':
            return CreatePromotionSerializer
        elif self.action == 'apply':
            return ApplyPromotionSerializer
        return PromotionSerializer
    
    def get_queryset(self):
        """Filtrer les promotions selon le context"""
        queryset = Promotion.objects.all()
        
        # Les utilisateurs normaux ne voient que les promos actives
        if self.request.user and not self.request.user.is_staff:
            queryset = queryset.filter(status=PromoStatus.ACTIVE)
        
        # Filtrer par type si paramètre fourni
        promo_type = self.request.query_params.get('type')
        if promo_type:
            queryset = queryset.filter(promo_type=promo_type)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Récupérer uniquement les promotions actives avec filtres"""
        queryset = Promotion.objects.filter(status=PromoStatus.ACTIVE)
        
        # Filtrer les promos valides temporellement
        now = timezone.now()
        queryset = queryset.filter(
            start_date__lte=now
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        )
        
        # Filtrer par usage_count
        queryset = queryset.filter(
            Q(max_uses__isnull=True) | Q(usage_count__lt=F('max_uses'))
        )
        
        # Trier par priorité
        queryset = queryset.order_by('-priority', '-created_at')
        
        serializer = PromotionListSerializer(queryset, many=True)
        return Response({'results': serializer.data})
    
    @action(detail=False, methods=['post'])
    def apply(self, request):
        """
        Appliquer une promotion à un trajet
        POST /promotions/apply/
        {
            "code": "MOVE25",
            "trip_amount": 5000,
            "user_id": "user123",
            "trip_id": "trip456",
            "covoiturage": false,
            "bagages": false
        }
        """
        serializer = ApplyPromotionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'message': 'Données invalides',
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            promotion = Promotion.objects.get(code=serializer.validated_data['code'])
            
            # Vérifier la validité
            if not promotion.is_valid():
                return Response(
                    {
                        'success': False,
                        'message': 'Cette promotion n\'est pas valide ou a expiré.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifier les conditions d'applicabilité
            trip_amount = serializer.validated_data['trip_amount']
            covoiturage = serializer.validated_data.get('covoiturage', False)
            bagages = serializer.validated_data.get('bagages', False)
            
            if covoiturage and not promotion.applicable_to_covoiturage:
                return Response(
                    {
                        'success': False,
                        'message': 'Cette promotion ne s\'applique pas au covoiturage.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if bagages and not promotion.applicable_to_bagages:
                return Response(
                    {
                        'success': False,
                        'message': 'Cette promotion ne s\'applique pas aux bagages.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculer la réduction
            discount = promotion.calculate_discount(trip_amount)
            
            if discount == 0:
                return Response(
                    {
                        'success': False,
                        'message': 'Montant minimum requis non atteint.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifier les utilisations par utilisateur
            user_id = serializer.validated_data['user_id']
            user_usage_count = UserPromotionUsage.objects.filter(
                user_id=user_id,
                promotion=promotion
            ).count()
            
            if user_usage_count >= promotion.max_uses_per_user:
                return Response(
                    {
                        'success': False,
                        'message': f'Vous avez déjà utilisé cette promotion {promotion.max_uses_per_user} fois.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Créer l'enregistrement d'utilisation
            final_amount = trip_amount - discount
            
            # Calculer le cashback MOVECoin
            cashback = (final_amount * promotion.cashback_percentage) / 100
            
            usage = UserPromotionUsage.objects.create(
                user_id=user_id,
                promotion=promotion,
                discount_applied=discount,
                trip_amount=trip_amount,
                trip_id=serializer.validated_data.get('trip_id', '')
            )
            
            # Incrémenter le compteur d'utilisation
            promotion.usage_count += 1
            promotion.save()
            
            return Response(
                {
                    'success': True,
                    'message': 'Promotion appliquée avec succès!',
                    'promotion_code': promotion.code,
                    'original_amount': float(trip_amount),
                    'discount_amount': float(discount),
                    'final_amount': float(final_amount),
                    'cashback_movecoin': float(cashback),
                },
                status=status.HTTP_200_OK
            )
        
        except Promotion.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Code promotionnel non trouvé.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f'Erreur: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Récupérer les statistiques des promotions (admin)
        GET /promotions/stats/?promo_type=covoiturage
        """
        queryset = Promotion.objects.all()
        
        promo_type = request.query_params.get('type')
        if promo_type:
            queryset = queryset.filter(promo_type=promo_type)
        
        stats = {
            'total_promotions': queryset.count(),
            'active_promotions': queryset.filter(status='active').count(),
            'draft_promotions': queryset.filter(status='draft').count(),
            'paused_promotions': queryset.filter(status='paused').count(),
            'total_usages': sum(p.usage_count for p in queryset),
            'total_discount_given': sum(
                sum(u.discount_applied for u in p.usages.all())
                for p in queryset
            ),
            'promotions_by_type': dict(
                queryset.values('promo_type').annotate(count=Count('id')).values_list('promo_type', 'count')
            ),
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activer une promotion"""
        promotion = self.get_object()
        promotion.status = PromoStatus.ACTIVE
        promotion.save()
        
        serializer = self.get_serializer(promotion)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Mettre en pause une promotion"""
        promotion = self.get_object()
        promotion.status = PromoStatus.PAUSED
        promotion.save()
        
        serializer = self.get_serializer(promotion)
        return Response(serializer.data)


class UserPromotionUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour voir l'historique d'utilisation des promotions
    - GET /promotion-usages/ : Lister
    - GET /promotion-usages/{id}/ : Détails
    """
    
    serializer_class = UserPromotionUsageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Les utilisateurs voient uniquement leurs utilisations"""
        user_id = self.request.query_params.get('user_id')
        
        if self.request.user.is_staff:
            # Admin voit tout
            return UserPromotionUsage.objects.all()
        
        # Les utilisateurs ne voient que leurs propres usages
        if user_id:
            return UserPromotionUsage.objects.filter(user_id=user_id)
        
        return UserPromotionUsage.objects.none()

