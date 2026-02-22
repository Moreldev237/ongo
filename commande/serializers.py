from rest_framework import serializers
from .models import Order, Location, OrderStatusHistory, OrderReview, VehicleType, OrderStatus, PaymentMethod


class LocationSerializer(serializers.ModelSerializer):
    """Serializer pour les localisations"""
    
    class Meta:
        model = Location
        fields = [
            'id',
            'address',
            'latitude',
            'longitude',
            'landmark',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer pour l'historique des statuts"""
    
    from_status_display = serializers.CharField(source='get_from_status_display', read_only=True)
    to_status_display = serializers.CharField(source='get_to_status_display', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = [
            'id',
            'from_status',
            'from_status_display',
            'to_status',
            'to_status_display',
            'changed_by',
            'reason',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class OrderReviewSerializer(serializers.ModelSerializer):
    """Serializer pour les avis"""
    
    class Meta:
        model = OrderReview
        fields = [
            'id',
            'client_rating',
            'client_review',
            'client_reviewed_at',
            'driver_rating',
            'driver_review',
            'driver_reviewed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les listes"""
    
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'reference',
            'user_id',
            'driver_id',
            'vehicle_type',
            'vehicle_type_display',
            'status',
            'status_display',
            'total_price',
            'payment_status',
            'created_at',
            'completed_at',
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les commandes"""
    
    pickup_location = LocationSerializer(read_only=True)
    dropoff_location = LocationSerializer(read_only=True)
    
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    review = OrderReviewSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'reference',
            'user_id',
            'driver_id',
            'pickup_location',
            'dropoff_location',
            'estimated_distance',
            'actual_distance',
            'estimated_time',
            'actual_time',
            'vehicle_type',
            'vehicle_type_display',
            'vehicle_number',
            'is_covoiturage',
            'is_bagages',
            'base_price',
            'covoiturage_discount',
            'bagages_surcharge',
            'promotion_discount',
            'tip_amount',
            'total_price',
            'payment_method',
            'payment_method_display',
            'payment_status',
            'payment_status_display',
            'paid_amount',
            'movecoin_earned',
            'driver_movecoin_earned',
            'status',
            'status_display',
            'user_notes',
            'driver_notes',
            'admin_notes',
            'scheduled_time',
            'created_at',
            'confirmed_at',
            'accepted_at',
            'started_at',
            'completed_at',
            'cancelled_at',
            'user_rating',
            'user_review',
            'driver_rating',
            'driver_review',
            'status_history',
            'review',
        ]
        read_only_fields = [
            'id',
            'reference',
            'created_at',
            'confirmed_at',
            'accepted_at',
            'started_at',
            'completed_at',
            'cancelled_at',
            'status_history',
            'review',
        ]


class CreateOrderSerializer(serializers.Serializer):
    """Serializer pour créer une commande"""
    
    user_id = serializers.CharField(max_length=100)
    
    pickup_location_id = serializers.IntegerField(required=False)
    pickup_address = serializers.CharField(max_length=500, required=False)
    pickup_latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    pickup_longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    pickup_landmark = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    dropoff_location_id = serializers.IntegerField(required=False)
    dropoff_address = serializers.CharField(max_length=500, required=False)
    dropoff_latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    dropoff_longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    dropoff_landmark = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    vehicle_type = serializers.ChoiceField(choices=VehicleType.choices, default=VehicleType.TAXI)
    
    estimated_distance = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    estimated_time = serializers.IntegerField(required=False)
    
    is_covoiturage = serializers.BooleanField(default=False)
    is_bagages = serializers.BooleanField(default=False)
    
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=PaymentMethod.choices, default=PaymentMethod.MOVECOIN)
    
    scheduled_time = serializers.DateTimeField(required=False, allow_null=True)
    user_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validations croisées"""
        # Vérifier que les localisations sont fournies
        has_pickup_location = data.get('pickup_location_id') or all([
            data.get('pickup_address'),
            data.get('pickup_latitude'),
            data.get('pickup_longitude')
        ])
        
        has_dropoff_location = data.get('dropoff_location_id') or all([
            data.get('dropoff_address'),
            data.get('dropoff_latitude'),
            data.get('dropoff_longitude')
        ])
        
        if not has_pickup_location:
            raise serializers.ValidationError("Localisation de départ requise")
        
        if not has_dropoff_location:
            raise serializers.ValidationError("Localisation d'arrivée requise")
        
        return data


class UpdateOrderStatusSerializer(serializers.Serializer):
    """Serializer pour mettre à jour le statut d'une commande"""
    
    new_status = serializers.ChoiceField(choices=OrderStatus.choices)
    changed_by = serializers.CharField(max_length=100)
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate_new_status(self, value):
        """Vérifier que le nouveau statut est valide"""
        valid_statuses = [choice[0] for choice in OrderStatus.choices]
        if value not in valid_statuses:
            raise serializers.ValidationError("Statut invalide")
        return value


class RateOrderSerializer(serializers.Serializer):
    """Serializer pour évaluer une commande"""
    
    rating = serializers.IntegerField(
        min_value=1,
        max_value=5,
        help_text="Note de 1 à 5"
    )
    review = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Commentaire optionnel"
    )
    reviewer_type = serializers.ChoiceField(
        choices=['client', 'driver'],
        help_text="Qui évalue (client ou driver)"
    )


class OrderStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques"""
    
    total_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    total_distance = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_time = serializers.IntegerField()
