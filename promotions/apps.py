from django.apps import AppConfig


class PromotionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'promotions'
    verbose_name = 'Promotions & Réductions'
    
    def ready(self):
        """Charger les signaux au démarrage"""
        import promotions.signals
