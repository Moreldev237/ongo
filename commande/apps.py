from django.apps import AppConfig


class CommandeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'commande'
    verbose_name = 'Commandes de Transport'
    
    def ready(self):
        """Charger les signaux au démarrage"""
        import commande.signals
