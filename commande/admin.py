from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Avg, Count
from .models import (
    Order, Location, OrderStatusHistory, OrderReview,
    VehicleType, OrderStatus, PaymentMethod, PaymentStatus
)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin pour les localisations"""
    
    list_display = [
        'address',
        'landmark',
        'coordinates',
        'created_at'
    ]
    
    list_filter = ['created_at']
    search_fields = ['address', 'landmark']
    
    def coordinates(self, obj):
        """Afficher les coordonnées GPS"""
        return f"({obj.latitude}, {obj.longitude})"
    coordinates.short_description = 'Coordonnées GPS'


class OrderStatusHistoryInline(admin.TabularInline):
    """Inline pour l'historique des statuts"""
    
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['from_status', 'to_status', 'changed_by', 'reason', 'created_at']
    
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class OrderReviewInline(admin.StackedInline):
    """Inline pour les avis"""
    
    model = OrderReview
    extra = 0
    fieldsets = (
        ('Avis Client', {
            'fields': ('client_rating', 'client_review', 'client_reviewed_at'),
        }),
        ('Avis Chauffeur', {
            'fields': ('driver_rating', 'driver_review', 'driver_reviewed_at'),
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin pour les commandes avec historique complet"""

    list_display = [
        'reference_link',
        'user_badge',
        'driver_badge',
        'vehicle_display',
        'route_display',
        'status_badge',
        'price_display',
        'payment_status_badge',
        'created_at_short'
    ]
    
    list_filter = [
        'status',
        'payment_status',
        'vehicle_type',
        'is_covoiturage',
        'is_bagages',
        'created_at',
        'completed_at'
    ]
    
    search_fields = [
        'reference',
        'user_id',
        'driver_id',
        'pickup_location__address',
        'dropoff_location__address'
    ]
    
    readonly_fields = [
        'reference',
        'created_at',
        'confirmed_at',
        'accepted_at',
        'started_at',
        'completed_at',
        'cancelled_at',
        'status_history_display',
        'price_breakdown',
        'trip_stats',
    ]
    
    fieldsets = (
        ('Informations Commande', {
            'fields': ('reference', 'user_id', 'driver_id', 'status'),
        }),
        ('Route', {
            'fields': ('pickup_location', 'dropoff_location', 'estimated_distance', 'actual_distance', 'estimated_time', 'actual_time'),
        }),
        ('Véhicule', {
            'fields': ('vehicle_type', 'vehicle_number', 'is_covoiturage', 'is_bagages'),
        }),
        ('Tarification', {
            'fields': ('base_price', 'covoiturage_discount', 'bagages_surcharge', 'promotion_discount', 'tip_amount', 'total_price'),
            'classes': ('collapse',),
        }),
        ('Détail Tarification', {
            'fields': ('price_breakdown',),
            'classes': ('collapse',),
        }),
        ('Paiement', {
            'fields': ('payment_method', 'payment_status', 'paid_amount', 'movecoin_earned', 'driver_movecoin_earned'),
        }),
        ('Chronologie', {
            'fields': ('created_at', 'confirmed_at', 'accepted_at', 'started_at', 'completed_at', 'cancelled_at'),
            'classes': ('collapse',),
        }),
        ('Statistiques Trajet', {
            'fields': ('trip_stats',),
            'classes': ('collapse',),
        }),
        ('Notes', {
            'fields': ('user_notes', 'driver_notes', 'admin_notes'),
            'classes': ('collapse',),
        }),
        ('Évaluations', {
            'fields': ('user_rating', 'user_review', 'driver_rating', 'driver_review'),
            'classes': ('collapse',),
        }),
        ('Historique Statuts', {
            'fields': ('status_history_display',),
        }),
    )
    
    inlines = [OrderStatusHistoryInline, OrderReviewInline]
    
    date_hierarchy = 'created_at'
    actions = ['mark_completed', 'mark_cancelled', 'export_orders']
    
    def reference_link(self, obj):
        """Afficher la référence avec lien"""
        url = reverse('admin:commande_order_change', args=[obj.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.reference
        )
    reference_link.short_description = 'Référence'
    
    def user_badge(self, obj):
        """Badge utilisateur"""
        return format_html(
            '<span style="background-color: #e3f2fd; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            obj.user_id
        )
    user_badge.short_description = 'Client'
    
    def driver_badge(self, obj):
        """Badge chauffeur"""
        if not obj.driver_id:
            return format_html(
                '<span style="color: #999;">Non assigné</span>'
            )
        return format_html(
            '<span style="background-color: #f3e5f5; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            obj.driver_id
        )
    driver_badge.short_description = 'Chauffeur'
    
    def vehicle_display(self, obj):
        """Afficher le type de véhicule avec emoji"""
        return obj.get_vehicle_type_display()
    vehicle_display.short_description = 'Véhicule'
    
    def route_display(self, obj):
        """Afficher la route"""
        return format_html(
            '{} → {}',
            obj.pickup_location.address[:20] + '...' if len(obj.pickup_location.address) > 20 else obj.pickup_location.address,
            obj.dropoff_location.address[:20] + '...' if len(obj.dropoff_location.address) > 20 else obj.dropoff_location.address
        )
    route_display.short_description = 'Route'
    
    def status_badge(self, obj):
        """Badge statut coloré"""
        colors = {
            'pending': '#ff9800',
            'confirmed': '#2196f3',
            'accepted': '#9c27b0',
            'driver_arriving': '#3f51b5',
            'driver_arrived': '#00bcd4',
            'in_progress': '#4caf50',
            'completed': '#8bc34a',
            'cancelled_user': '#ef5350',
            'cancelled_driver': '#ef5350',
            'cancelled_admin': '#ef5350',
            'no_show': '#795548',
        }
        color = colors.get(obj.status, '#757575')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def price_display(self, obj):
        """Afficher le prix"""
        return format_html(
            '<span style="color: #2e7d32; font-weight: bold;">{} XAF</span>',
            int(obj.total_price)
        )
    price_display.short_description = 'Montant'
    
    def payment_status_badge(self, obj):
        """Badge statut paiement"""
        colors = {
            'pending': '#ff9800',
            'completed': '#4caf50',
            'failed': '#ef5350',
            'refunded': '#2196f3',
        }
        color = colors.get(obj.payment_status, '#757575')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Paiement'
    
    def created_at_short(self, obj):
        """Date courte"""
        return obj.created_at.strftime('%d/%m %H:%M')
    created_at_short.short_description = 'Créée le'
    
    def price_breakdown(self, obj):
        """Afficher le détail du prix"""
        html = f"""
        <table style="width: 100%; border-collapse: collapse;">
            <tr><td>Tarif de base:</td><td style="text-align: right; font-weight: bold;">{int(obj.base_price)} XAF</td></tr>
            <tr><td style="color: green;">- Réduction covoiturage:</td><td style="text-align: right; color: green;">-{int(obj.covoiturage_discount)} XAF</td></tr>
            <tr><td>+ Surcharge bagages:</td><td style="text-align: right;">+{int(obj.bagages_surcharge)} XAF</td></tr>
            <tr><td style="color: green;">- Réduction promotion:</td><td style="text-align: right; color: green;">-{int(obj.promotion_discount)} XAF</td></tr>
            <tr><td>+ Pourboire:</td><td style="text-align: right;">+{int(obj.tip_amount)} XAF</td></tr>
            <tr style="border-top: 2px solid #333;"><td style="font-weight: bold;">TOTAL:</td><td style="text-align: right; font-weight: bold; font-size: 1.2em;">{int(obj.total_price)} XAF</td></tr>
        </table>
        <hr>
        <div style="margin-top: 10px;">
            <strong>Paiement:</strong><br>
            Méthode: {obj.get_payment_method_display()}<br>
            Payé: {int(obj.paid_amount)} XAF<br>
            MOVECoin gagné (client): {obj.movecoin_earned}<br>
            MOVECoin gagné (chauffeur): {obj.driver_movecoin_earned}
        </div>
        """
        return format_html(html)
    price_breakdown.short_description = 'Détail Tarification'
    
    def trip_stats(self, obj):
        """Afficher les statistiques du trajet"""
        html = f"""
        <table style="width: 100%; border-collapse: collapse;">
            <tr><td>Distance estimée:</td><td style="text-align: right;">{obj.estimated_distance} km</td></tr>
            <tr><td>Distance réelle:</td><td style="text-align: right;">{obj.actual_distance or 'N/A'} km</td></tr>
            <tr><td>Temps estimé:</td><td style="text-align: right;">{obj.estimated_time or 'N/A'} min</td></tr>
            <tr><td>Temps réel:</td><td style="text-align: right;">{obj.actual_time or 'N/A'} min</td></tr>
        </table>
        """
        return format_html(html)
    trip_stats.short_description = 'Statistiques Trajet'
    
    def status_history_display(self, obj):
        """Afficher l'historique des statuts"""
        history = obj.status_history.all()
        if not history:
            return 'Pas d\'historique'
        
        html = '<table style="width: 100%; border-collapse: collapse; font-size: 12px;">'
        html += '<thead><tr style="background-color: #f0f0f0;"><th style="text-align: left; padding: 8px;">De</th><th style="text-align: left; padding: 8px;">À</th><th style="text-align: left; padding: 8px;">Par</th><th style="text-align: left; padding: 8px;">Date</th><th style="text-align: left; padding: 8px;">Raison</th></tr></thead>'
        html += '<tbody>'
        
        for h in history:
            html += f'<tr style="border-bottom: 1px solid #ddd;"><td style="padding: 8px;">{h.get_from_status_display() if h.from_status else "—"}</td><td style="padding: 8px;"><strong>{h.get_to_status_display()}</strong></td><td style="padding: 8px;">{h.changed_by}</td><td style="padding: 8px;">{h.created_at.strftime("%d/%m %H:%M")}</td><td style="padding: 8px;">{h.reason}</td></tr>'
        
        html += '</tbody></table>'
        return format_html(html)
    status_history_display.short_description = 'Historique des changements de statut'
    
    def mark_completed(self, request, queryset):
        """Action pour marquer comme complétée"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} commande(s) marquée(s) comme complétée(s).')
    mark_completed.short_description = "Marquer comme complétée"
    
    def mark_cancelled(self, request, queryset):
        """Action pour annuler"""
        updated = queryset.update(status='cancelled_admin')
        self.message_user(request, f'{updated} commande(s) annulée(s).')
    mark_cancelled.short_description = "Annuler la commande"
    
    def export_orders(self, request, queryset):
        """Action pour exporter les commandes"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Référence', 'Client', 'Chauffeur', 'Statut', 'Montant', 'Paiement', 'Date'])
        
        for order in queryset:
            writer.writerow([
                order.reference,
                order.user_id,
                order.driver_id or '—',
                order.get_status_display(),
                order.total_price,
                order.get_payment_status_display(),
                order.created_at.strftime('%d/%m/%Y %H:%M')
            ])
        
        return response
    export_orders.short_description = "Exporter les commandes sélectionnées"


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """Admin pour l'historique des statuts"""
    
    list_display = [
        'order_link',
        'from_status_display',
        'to_status_display',
        'changed_by',
        'created_at'
    ]
    
    list_filter = ['created_at', 'to_status']
    search_fields = ['order__reference', 'changed_by']
    readonly_fields = ['order', 'from_status', 'to_status', 'changed_by', 'reason', 'created_at']
    
    def order_link(self, obj):
        """Lien vers la commande"""
        url = reverse('admin:commande_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', url, obj.order.reference)
    order_link.short_description = 'Commande'
    
    def from_status_display(self, obj):
        """Afficher le statut initial"""
        if obj.from_status:
            for choice in OrderStatus.choices:
                if choice[0] == obj.from_status:
                    return choice[1]
        return '—'
    from_status_display.short_description = 'De'
    
    def to_status_display(self, obj):
        """Afficher le statut final"""
        for choice in OrderStatus.choices:
            if choice[0] == obj.to_status:
                return choice[1]
        return obj.to_status
    to_status_display.short_description = 'À'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OrderReview)
class OrderReviewAdmin(admin.ModelAdmin):
    """Admin pour les avis"""
    
    list_display = [
        'order_link',
        'client_rating_display',
        'driver_rating_display',
        'updated_at'
    ]
    
    list_filter = ['client_rating', 'driver_rating', 'updated_at']
    search_fields = ['order__reference']
    readonly_fields = ['order', 'created_at', 'updated_at']
    
    def order_link(self, obj):
        """Lien vers la commande"""
        url = reverse('admin:commande_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', url, obj.order.reference)
    order_link.short_description = 'Commande'
    
    def client_rating_display(self, obj):
        """Afficher la note client avec étoiles"""
        if obj.client_rating:
            stars = '⭐' * obj.client_rating
            return format_html('{} ({}/5)', stars, obj.client_rating)
        return '—'
    client_rating_display.short_description = 'Note Client'
    
    def driver_rating_display(self, obj):
        """Afficher la note chauffeur avec étoiles"""
        if obj.driver_rating:
            stars = '⭐' * obj.driver_rating
            return format_html('{} ({}/5)', stars, obj.driver_rating)
        return '—'
    driver_rating_display.short_description = 'Note Chauffeur'
