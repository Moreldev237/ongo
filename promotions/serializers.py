from rest_framework import serializers
from .models import Promotion, UserPromotionUsage, PromotionType, PromoStatus


class PromotionSerializer(serializers.ModelSerializer):
    """Serializer pour les promotions"""
    
    promo_type_display = serializers.CharField(source='get_promo_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)
    target_users_display = serializers.CharField(source='get_target_users_display', read_only=True)
    
    class Meta:
        model = Promotion
        fields = [
            'id',
            'code',
            'name',
            'description',
            'promo_type',
            'promo_type_display',
            'status',
            'status_display',
            'discount_type',
            'discount_type_display',
            'discount_value',
            'max_discount',
            'min_amount',
            'start_date',
            'end_date',
            'max_uses',
            'max_uses_per_user',
            'usage_count',
            'target_users',
            'target_users_display',
            'applicable_to_covoiturage',
            'applicable_to_bagages',
            'cashback_percentage',
            'priority',
            'created_at',
            'updated_at',
            'created_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'usage_count']


class PromotionDetailSerializer(PromotionSerializer):
    """Serializer détaillé avec les statistiques d'utilisation"""
    
    usages = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    
    def get_usages(self, obj):
        """Récupérer les dernières utilisations"""
        usages = obj.usages.all()[:10]  # Dernières 10 utilisations
        return UserPromotionUsageSerializer(usages, many=True).data
    
    def get_is_valid(self, obj):
        """Vérifier si la promotion est valide"""
        return obj.is_valid()
    
    class Meta(PromotionSerializer.Meta):
        fields = PromotionSerializer.Meta.fields + ['usages', 'is_valid']


class PromotionListSerializer(PromotionSerializer):
    """Serializer simplifié pour les listes"""
    
    class Meta:
        model = Promotion
        fields = [
            'id',
            'code',
            'name',
            'promo_type',
            'promo_type_display',
            'discount_type',
            'discount_value',
            'status',
            'status_display',
            'priority',
        ]


class UserPromotionUsageSerializer(serializers.ModelSerializer):
    """Serializer pour l'historique d'utilisation"""
    
    promotion_code = serializers.CharField(source='promotion.code', read_only=True)
    promotion_name = serializers.CharField(source='promotion.name', read_only=True)
    
    class Meta:
        model = UserPromotionUsage
        fields = [
            'id',
            'user_id',
            'promotion',
            'promotion_code',
            'promotion_name',
            'used_at',
            'discount_applied',
            'trip_amount',
            'trip_id',
        ]
        read_only_fields = ['id', 'used_at']


class ApplyPromotionSerializer(serializers.Serializer):
    """Serializer pour appliquer une promotion à un trajet"""
    
    code = serializers.CharField(max_length=50)
    trip_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    user_id = serializers.CharField(max_length=100)
    trip_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    covoiturage = serializers.BooleanField(default=False)
    bagages = serializers.BooleanField(default=False)
    
    def validate_code(self, value):
        """Vérifier que le code existe"""
        try:
            promotion = Promotion.objects.get(code=value.upper())
            if not promotion.is_valid():
                raise serializers.ValidationError("Cette promotion n'est pas valide.")
            return value.upper()
        except Promotion.DoesNotExist:
            raise serializers.ValidationError("Code promotionnel invalide.")
    
    def validate_trip_amount(self, value):
        """Vérifier que le montant est positif"""
        if value <= 0:
            raise serializers.ValidationError("Le montant du trajet doit être positif.")
        return value


class PromotionResponseSerializer(serializers.Serializer):
    """Réponse après application d'une promotion"""
    
    success = serializers.BooleanField()
    message = serializers.CharField()
    promotion_code = serializers.CharField(required=False)
    original_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    final_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    cashback_movecoin = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)


class CreatePromotionSerializer(serializers.ModelSerializer):
    """Serializer pour créer une promotion (admin)"""
    
    class Meta:
        model = Promotion
        fields = [
            'code',
            'name',
            'description',
            'promo_type',
            'status',
            'discount_type',
            'discount_value',
            'max_discount',
            'min_amount',
            'start_date',
            'end_date',
            'max_uses',
            'max_uses_per_user',
            'target_users',
            'applicable_to_covoiturage',
            'applicable_to_bagages',
            'cashback_percentage',
            'priority',
            'created_by',
        ]
    
    def validate_code(self, value):
        """Code doit être unique et en majuscules"""
        if Promotion.objects.filter(code=value.upper()).exists():
            raise serializers.ValidationError("Ce code promotionnel existe déjà.")
        return value.upper()
    
    def validate(self, data):
        """Validations croisées"""
        if data.get('end_date') and data.get('start_date') >= data.get('end_date'):
            raise serializers.ValidationError("La date de fin doit être après la date de début.")
        
        if data.get('max_discount') and data.get('discount_type') == 'fixed':
            raise serializers.ValidationError("max_discount ne s'applique pas aux réductions fixes.")
        
        return data
