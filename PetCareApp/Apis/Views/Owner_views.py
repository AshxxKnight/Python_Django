import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http.response import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
import logging
from Apis.models.Provider_models import Service, ServiceProvider
from ..models.Owner_models import Favorites, Order, Owner, Cart
from ..Serializers.Owner_serializers import CartSerializer, FavoritesSerializer, OrderSerializer, OwnerSerializer

logger = logging.getLogger(__name__)

# Fetch the profile of the logged-in user
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def owner_profile(request):
    try:
        owner = request.user.owner
    except Owner.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = OwnerSerializer(owner)
    return Response(serializer.data)

@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_owner_profile(request):
    try:
        owner = request.user.owner
    except Owner.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = JSONParser().parse(request)
    # Ensure the email field is not considered if it hasn't changed
    if 'email' in data and data['email'] == owner.email:
        data.pop('email')

    serializer = OwnerSerializer(owner, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Register a new owner
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_owner(request):
    data = JSONParser().parse(request)
    
    email = data.get('email')
    password = data.get('password')
    owner_name = data.get('owner_name')
    pet_name = data.get('pet_name')
    address = data.get('address')
    phone_number = data.get('phone_number')
    pet_age = data.get('pet_age')
    animal_type = data.get('animal_type')
    username = data.get('username')
    
    # Hash the password
    hashed_password = make_password(password)
    
    # Create a new owner instance
    owner = Owner(
        email=email,
        password=hashed_password,
        owner_name=owner_name,
        pet_name=pet_name,
        address=address,
        phone_number=phone_number,
        pet_age=pet_age,
        animal_type=animal_type,
        username=username
    )
    
    owner.save()
    
    serializer = OwnerSerializer(owner)
    return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    data = JSONParser().parse(request)
    email = data.get('email')
    password = data.get('password')

    user = authenticate(username=email, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({"token": token.key}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


##########################################################################


# Cart functions

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_service_to_cart(request):
    try:
        data = JSONParser().parse(request)
    except Exception as e:
        logger.error(f'Error parsing data: {str(e)}')
        return Response({'error': f'Error parsing data: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Ensure data is a dictionary
    if not isinstance(data, dict):
        logger.error('Invalid data format')
        return Response({'error': 'Invalid data format'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if 'service_id' is in the data
    if 'service_id' not in data:
        logger.error('service_id is required')
        return Response({'error': 'service_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    service_id = data['service_id']
    
    try:
        # Fetch the service details
        service = Service.objects.get(service_id=service_id)
        
        # Fetch the provider details
        provider = service.provider
        
        # Construct the cart data
        cart_data = {
            'owner': request.user.owner.owner_id,
            'service_id': service.service_id,
            'service_name': service.service_name,
            'scheduled_date_time': data.get('scheduled_date_time', timezone.now()),
            'service_provider_name': provider.name,
            'service_charges': service.price
        }
        
        # Serialize the cart data
        serializer = CartSerializer(data=cart_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f'Serializer errors: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Service.DoesNotExist:
        logger.error('Service not found')
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except ServiceProvider.DoesNotExist:
        logger.error('Provider not found')
        return Response({'error': 'Provider not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

# Delete Service from Cart
@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_service_from_cart(request, cart_id):
    try:
        cart_item = Cart.objects.get(cart_id=cart_id, owner=request.user.owner)
    except Cart.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    cart_item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# Update Scheduled Time
@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_scheduled_time(request, cart_id):
    try:
        cart_item = Cart.objects.get(cart_id=cart_id, owner=request.user.owner)
    except Cart.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    data = JSONParser().parse(request)
    serializer = CartSerializer(cart_item, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_cart_items(request):
    owner = request.user.owner
    cart_items = Cart.objects.filter(owner=owner)
    serializer = CartSerializer(cart_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#################################################################

# Order Functions


# Place an order
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    try:
        owner = request.user.owner
    except Owner.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = JSONParser().parse(request)
    cart_items = Cart.objects.filter(owner=owner)

    if not cart_items.exists():
        return Response({"detail": "No items in cart"}, status=status.HTTP_400_BAD_REQUEST)

    for item in cart_items:
        order_data = {
            "owner": owner.owner_id,
            "service_id": item.service_id,
            "service_name": item.service_name,
            "scheduled_date_time": item.scheduled_date_time,
            "service_provider_name": item.service_provider_name,
            "service_charges": item.service_charges,
            "status": "Placed"
        }
        serializer = OrderSerializer(data=order_data)
        if serializer.is_valid():
            serializer.save()
            item.delete()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail": "Order placed successfully"}, status=status.HTTP_201_CREATED)


# View order status
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_order_status(request, order_id):
    try:
        owner = request.user.owner
        order = Order.objects.get(order_id=order_id, owner=owner)
    except (Owner.DoesNotExist, Order.DoesNotExist):
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = OrderSerializer(order)
    return Response(serializer.data)


# Cancel an order
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    try:
        owner = request.user.owner
        order = Order.objects.get(order_id=order_id, owner=owner)
    except (Owner.DoesNotExist, Order.DoesNotExist):
        return Response(status=status.HTTP_404_NOT_FOUND)

    if order.status == 'Placed':
        order.status = 'Cancelled'
        order.save()
        return Response({"detail": "Order cancelled successfully"}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Order cannot be cancelled"}, status=status.HTTP_400_BAD_REQUEST)


# Search orders by service name
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_orders(request):
    service_name = request.query_params.get('service_name', '').strip().lower()
    owner = request.user.owner
    orders = Order.objects.filter(owner=owner, service_name__icontains=service_name)
    if not orders:
        return Response({"detail": "No orders found matching the service name."}, status=status.HTTP_404_NOT_FOUND)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


# View all orders for logged-in owner
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_orders(request):
    try:
        owner = request.user.owner
    except Owner.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    orders = Order.objects.filter(owner=owner)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

###############################################################

# Review

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request, service_id):
    try:
        service = Service.objects.get(service_id=service_id)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    data = JSONParser().parse(request)
    review = data.get('review')

    if not review:
        return Response({"error": "Review is required"}, status=status.HTTP_400_BAD_REQUEST)

    reviews = service.get_reviews()
    reviews.append(review)
    service.reviews = json.dumps(reviews)
    service.save()

    return Response({"message": "Review added successfully", "reviews": reviews}, status=status.HTTP_200_OK)

##################################

#Favorite

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_service_to_favorites(request):
    try:
        data = JSONParser().parse(request)
    except Exception as e:
        logger.error(f'Error parsing data: {str(e)}')
        return Response({'error': f'Error parsing data: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Ensure data is a dictionary
    if not isinstance(data, dict):
        logger.error('Invalid data format')
        return Response({'error': 'Invalid data format'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if 'service_id' is in the data
    if 'service_id' not in data:
        logger.error('service_id is required')
        return Response({'error': 'service_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    service_id = data['service_id']
    
    try:
        # Fetch the service details
        service = Service.objects.get(service_id=service_id)
        
        # Fetch the provider details
        provider = service.provider
        
        # Construct the favorite data
        favorite_data = {
            'owner': request.user.owner.owner_id,
            'service_name': service.service_name,
            'service_provider_name': provider.name
        }
        
        # Serialize the favorite data
        serializer = FavoritesSerializer(data=favorite_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f'Serializer errors: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Service.DoesNotExist:
        logger.error('Service not found')
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except ServiceProvider.DoesNotExist:
        logger.error('Provider not found')
        return Response({'error': 'Provider not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_favorite_items(request):
    try:
        # Get the logged-in user
        owner = request.user.owner
        
        # Fetch favorites for the logged-in user
        favorites_items = Favorites.objects.filter(owner=owner)
        
        # Serialize the data
        serializer = FavoritesSerializer(favorites_items, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        # Handle unexpected errors
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_favorite(request, favorite_id):
    try:
        favorite = Favorites.objects.get(favorites_id=favorite_id, owner=request.user.owner)
        favorite.delete()
        return JsonResponse({'message': 'Favorite deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Favorites.DoesNotExist:
        return JsonResponse({'error': 'Favorite not found'}, status=status.HTTP_404_NOT_FOUND)
