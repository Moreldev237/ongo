
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/utilisateurs/', include('utilisateurs.urls')),
     path('api/wallet/', include('wallet.urls')),
]
