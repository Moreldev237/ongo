
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/utilisateurs/', include('utilisateurs.urls')),
    path('api/wallet/', include('wallet.urls')),
    path('api/promotions/', include('promotions.urls')),
    path('api/commande/', include('commande.urls')),
]

# Serve frontend files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')

urlpatterns += [
    # Auth pages
    path('login/', TemplateView.as_view(template_name='login.html')),
    path('login.html', TemplateView.as_view(template_name='login.html')),
    path('register/', TemplateView.as_view(template_name='register.html')),
    path('register.html', TemplateView.as_view(template_name='register.html')),
    path('forgot-password/', TemplateView.as_view(template_name='forgot-password.html')),
    path('forgot-password.html', TemplateView.as_view(template_name='forgot-password.html')),
    path('reset-password/<str:uid>/<str:token>/', TemplateView.as_view(template_name='forgot-password.html')),
    
    # Dashboard pages
    path('', TemplateView.as_view(template_name='index.html')),
    path('index.html', TemplateView.as_view(template_name='index.html')),
    path('orders/', TemplateView.as_view(template_name='orders.html')),
    path('orders.html', TemplateView.as_view(template_name='orders.html')),
    path('create-order/', TemplateView.as_view(template_name='create-order.html')),
    path('create-order.html', TemplateView.as_view(template_name='create-order.html')),
    path('promotions/', TemplateView.as_view(template_name='promotions.html')),
    path('promotions.html', TemplateView.as_view(template_name='promotions.html')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=frontend_dir)
