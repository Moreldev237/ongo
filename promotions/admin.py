from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Promotion, UserPromotionUsage


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """Admin pour gérer les promotions"""
    
    list_display = [
        'code_colored',
        'name',
        'get_promo_type_display',
        'get_discount_display',
        'status_colored',
        'validity_status',
        'usage_count_display',
        'priority'
    ]
    
    list_filter = [
        'status',
        'promo_type',
        'discount_type',
        'applicable_to_covoiturage',
        'applicable_to_bagages',
        'created_at'
    ]
    
    search_fields = ['code', 'name', 'description']
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('code', 'name', 'description', 'promo_type', 'status', 'priority')
        }),
        ('Réduction', {
            'fields': ('discount_type', 'discount_value', 'max_discount', 'min_amount')
        }),
        ('Validité Temporelle', {
            'fields': ('start_date', 'end_date')
        }),
        ('Limitations', {
            'fields': ('max_uses', 'max_uses_per_user', 'usage_count')
        }),
        ('Ciblage', {
            'fields': ('target_users',)
        }),
        ('Conditions d\'Applicabilité', {
            'fields': ('applicable_to_covoiturage', 'applicable_to_bagages')
        }),
        ('MOVECoin', {
            'fields': ('cashback_percentage',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'usage_count', 'created_by']
    
    def code_colored(self, obj):
        """Afficher le code avec un badge coloré"""
        colors = {
            'draft': '#f0ad4e',
            'active': '#5cb85c',
            'paused': '#5bc0de',
            'expired': '#d9534f',
            'archived': '#777777',
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.code
        )
    code_colored.short_description = 'Code'
    
    def get_promo_type_display(self, obj):
        """Afficher le type de promo"""
        return obj.get_promo_type_display()
    get_promo_type_display.short_description = 'Type'
    
    def status_colored(self, obj):
        """Afficher le statut avec couleur"""
        colors = {
            'draft': '#f0ad4e',
            'active': '#5cb85c',
            'paused': '#5bc0de',
            'expired': '#d9534f',
            'archived': '#777777',
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Statut'
    
    def get_discount_display(self, obj):
        """Afficher la réduction"""
        if obj.discount_type == 'percentage':
            return f"{obj.discount_value}%"
        else:
            return f"{obj.discount_value} XAF"
    get_discount_display.short_description = 'Réduction'
    
    def validity_status(self, obj):
        """Afficher l'état de validité"""
        if obj.is_valid():
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Valide</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Invalide</span>'
            )
    validity_status.short_description = 'Validité'
    
    def usage_count_display(self, obj):
        """Afficher l'utilisation"""
        if obj.max_uses:
            percentage = (obj.usage_count / obj.max_uses) * 100
            return f"{obj.usage_count}/{obj.max_uses} ({percentage:.0f}%)"
        else:
            return f"{obj.usage_count}/∞"
    usage_count_display.short_description = 'Utilisations'
    
    def save_model(self, request, obj, form, change):
        """Ajouter l'admin courant comme créateur"""
        if not change:
            obj.created_by = request.user.username
        super().save_model(request, obj, form, change)
    
    actions = ['activate_promotions', 'pause_promotions', 'archive_promotions']
    
    def activate_promotions(self, request, queryset):
        """Action pour activer les promotions"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} promotion(s) activée(s).')
    activate_promotions.short_description = "Activer les promotions sélectionnées"
    
    def pause_promotions(self, request, queryset):
        """Action pour suspendre les promotions"""
        updated = queryset.update(status='paused')
        self.message_user(request, f'{updated} promotion(s) suspendue(s).')
    pause_promotions.short_description = "Suspendre les promotions sélectionnées"
    
    def archive_promotions(self, request, queryset):
        """Action pour archiver les promotions"""
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} promotion(s) archivée(s).')
    archive_promotions.short_description = "Archiver les promotions sélectionnées"


@admin.register(UserPromotionUsage)
class UserPromotionUsageAdmin(admin.ModelAdmin):
    """Admin pour voir l'historique d'utilisation"""
    
    list_display = [
        'user_id',
        'promotion',
        'discount_applied',
        'trip_amount',
        'used_at'
    ]
    
    list_filter = [
        'promotion',
        'used_at'
    ]
    
    search_fields = ['user_id', 'promotion__code', 'trip_id']
    
    readonly_fields = [
        'user_id',
        'promotion',
        'discount_applied',
        'trip_amount',
        'used_at',
        'trip_id'
    ]
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user_id', 'trip_id')
        }),
        ('Promotion', {
            'fields': ('promotion',)
        }),
        ('Montants', {
            'fields': ('trip_amount', 'discount_applied')
        }),
        ('Informations', {
            'fields': ('used_at',)
        }),
    )
    
    date_hierarchy = 'used_at'
    
    def has_add_permission(self, request):
        """Ne pas permettre l'ajout manuel"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Ne pas permettre la suppression"""
        return False

