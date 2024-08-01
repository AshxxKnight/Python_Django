from rest_framework import serializers
from ..models.Owner_models import Owner, Cart, Order, Favorites

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = [
            'owner_id',
            'owner_name',
            'pet_name',
            'email',
            'address',
            'phone_number',
            'pet_age',
            'animal_type'
        ]

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            'cart_id',
            'owner',
            'service_id',
            'service_name',
            'scheduled_date_time',
            'service_provider_name',
            'service_charges'
        ]

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'order_id',
            'owner',
            'service_id',
            'service_name',
            'scheduled_date_time',
            'service_provider_name',
            'service_charges',
            'status'
        ]

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

class FavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorites
        fields = [
            'favorites_id', 
            'owner',
            'service_name',
            'service_provider_name'
        ]
