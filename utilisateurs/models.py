from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, unique=True)
    movecoin_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
    

class DriverProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=20)
    vehicle_number = models.CharField(max_length=20)
    documents_submitted = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.vehicle_type}"
    

class Trip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='driver_trips')
    vehicle_type = models.CharField(max_length=20)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='EN_ATTENTE')  # PAYÉ / EN_ATTENTE / ANNULÉ
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trip {self.id} : {self.user.email} -> {self.destination}"