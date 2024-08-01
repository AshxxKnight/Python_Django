from django.db import models
from django.contrib.auth.models import AbstractUser
import json
from Apis.models.Users import User

# Create your models here.

# Service Provider Model
class ServiceProvider(User):
    provider_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    
    def __str__(self):
        return f'{self.email} - {self.name}'
    
    class Meta:
        permissions = [
            ("can_view_service_provider", "Can view service provider")
        ]
        

#Service Model
class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    service_name = models.CharField(max_length=100)
    reviews = models.TextField(default='[]') 
    is_todays_special = models.BooleanField(default=False)
    is_deal_of_the_day = models.BooleanField(default=False)

    def get_reviews(self):
        return json.loads(self.reviews)  

    def add_review(self, review):
        reviews = json.loads(self.reviews)
        reviews.append(review)
        self.reviews = json.dumps(reviews)
        self.save()

    def __str__(self):
        return self.service_name
