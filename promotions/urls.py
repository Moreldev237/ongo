from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PromotionViewSet, UserPromotionUsageViewSet

# Créer un router pour les ViewSets
router = DefaultRouter()
router.register(r'promotions', PromotionViewSet, basename='promotion')
router.register(r'promotion-usages', UserPromotionUsageViewSet, basename='promotion-usage')

urlpatterns = [
    path('', include(router.urls)),
]
