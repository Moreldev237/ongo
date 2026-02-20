from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DriverProfile, Trip

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'vehicle_type', 'vehicle_number', 'is_verified')
    search_fields = ('user__email', 'vehicle_number')

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('user', 'driver', 'vehicle_type', 'origin', 'destination', 'price', 'payment_status', 'date')
    search_fields = ('user__email', 'driver__email', 'origin', 'destination')