from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, LocationViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'locations', LocationViewSet, basename='location')

urlpatterns = [
    path('', include(router.urls)),
]
