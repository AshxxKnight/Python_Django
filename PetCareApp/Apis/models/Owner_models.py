from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser

from Apis.models.Users import User

# Create your models here.

# Pet Owner Model
class Owner(User):
    owner_id = models.AutoField(primary_key=True)
    owner_name = models.CharField(max_length=100)
    pet_name = models.CharField(max_length=100)
    pet_age = models.PositiveIntegerField()
    animal_type = models.CharField(max_length=50)
    
    def __str__(self):
        return f'{self.email} - {self.owner_name}'
    
    class Meta:
        permissions = [
            ("can_view_owner", "Can view owner")
        ]

        
# Cart Model
class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    service_id = models.IntegerField()
    service_name = models.CharField(max_length=100)
    scheduled_date_time = models.DateTimeField(default=timezone.now)
    service_provider_name = models.CharField(max_length=100)
    service_charges = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f'Cart {self.cart_id} - Service: {self.service_name}'
    
# Order Model
class Order(models.Model):
    STATUS_CHOICES = [
        ('Placed', 'Placed'),
        ('Processed', 'Processed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    order_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    service_id = models.IntegerField()
    service_name = models.CharField(max_length=100)
    scheduled_date_time = models.DateTimeField()
    service_provider_name = models.CharField(max_length=100)
    service_charges = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Placed')

    
    def __str__(self):
        return f'Order {self.order_id} - Service: {self.service_name}'

class Favorites(models.Model):
    favorites_id = models.AutoField(primary_key=True)  # Unique identifier for the favorite
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='favorites')
    service_name = models.CharField(max_length=100)
    service_provider_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f'{self.owner.owner_name} - {self.service_name}'