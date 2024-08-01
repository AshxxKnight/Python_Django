from rest_framework import serializers
from ..models.Provider_models import ServiceProvider, Service

class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = ['provider_id', 
                  'name', 
                  'email', 
                  'phone_number', 
                  'address',
                 'username', 
                 'password']

    
class ServiceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Service
        fields = ['service_id', 'service_name', 'description', 'price', 'provider', 'is_deal_of_the_day', 'is_todays_special', 'reviews']

    def get_provider_name(self, obj):
        return obj.provider.name if obj.provider else None


        