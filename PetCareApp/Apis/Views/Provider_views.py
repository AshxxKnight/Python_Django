from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http.response import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

from Apis.Serializers.Owner_serializers import OrderSerializer, OrderStatusUpdateSerializer
from Apis.models.Owner_models import Order
from ..models.Provider_models import ServiceProvider, Service
from ..Serializers.Provider_serializers import ServiceProviderSerializer, ServiceSerializer
from rest_framework.authtoken.models import Token

# Fetch the profile of the logged-in service provider
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def provider_profile(request):
    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ServiceProviderSerializer(provider)
    return Response(serializer.data)

# Update the profile of the logged-in service provider
@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_provider_profile(request):
    try:
        provider = request.user
    except ServiceProvider.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = JSONParser().parse(request)
    serializer = ServiceProviderSerializer(provider, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Register a new service provider
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_provider(request):
    data = JSONParser().parse(request)
    
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    phone_number = data.get('phone_number')
    address = data.get('address')
    username = data.get('username')
    
    # Hash the password
    hashed_password = make_password(password)
    
    # Create a new service provider instance
    provider = ServiceProvider(
        email=email,
        password=hashed_password,
        name=name,
        phone_number=phone_number,
        address=address,
        username=username
    )
    
    provider.save()
    
    serializer = ServiceProviderSerializer(provider)
    return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def provider_login_view(request):
    data = JSONParser().parse(request)
    email = data.get('email')
    password = data.get('password')

    user = authenticate(username=email, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({"token": token.key}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


########################################################################################################


# Create a new service
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_service(request):
    data = JSONParser().parse(request)
    data['provider'] = request.user.serviceprovider.provider_id
    serializer = ServiceSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Fetch all services
@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def list_services(request):
    services = Service.objects.all()
    response_data = []

    for service in services:
        provider = service.provider
        response_data.append({
            'service_id': service.service_id,
            'service_name': service.service_name,
            'description': service.description,
            'price': service.price,
            'provider_name': provider.name if provider else None,
            'is_deal_of_the_day': service.is_deal_of_the_day,
            'is_todays_special': service.is_todays_special,
            'reviews': service.reviews,
        })

    return Response(response_data)

#Fetch service of single provider
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_services_for_provider(request):
    # Get the logged-in user's provider profile
    try:
        provider = ServiceProvider.objects.get(id=request.user.id)
    except ServiceProvider.DoesNotExist:
        return Response({'error': 'User is not a service provider'}, status=status.HTTP_403_FORBIDDEN)

    # Filter services based on the logged-in provider
    services = Service.objects.filter(provider=provider)
    response_data = []

    for service in services:
        response_data.append({
            'service_id': service.service_id,
            'service_name': service.service_name,
            'description': service.description,
            'price': service.price,
            'provider_name': provider.name if provider else None,
            'is_deal_of_the_day': 'Yes' if service.is_deal_of_the_day else 'No',
            'is_todays_special': 'Yes' if service.is_todays_special else 'No',
            'reviews': service.reviews,
        })

    return Response(response_data)



# Fetch a single service by ID
@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_service(request, service_id):
    try:
        service = Service.objects.get(service_id=service_id)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ServiceSerializer(service)
    return Response(serializer.data)

# Update a service
@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_service(request, service_id):
    try:
        service = Service.objects.get(service_id=service_id)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = JSONParser().parse(request)
    
    # Ensure the provider field is set if not provided in the request data
    if 'provider' not in data:
        data['provider'] = service.provider.provider_id

    serializer = ServiceSerializer(service, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete a service
@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_service(request, service_id):
    try:
        service = Service.objects.get(service_id=service_id)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    service.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


#########################################################

# Manage orders

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_orders(request):
    try:
        service_provider = ServiceProvider.objects.get(id=request.user.id)
    except ServiceProvider.DoesNotExist:
        return Response({'error': 'Service provider not found'}, status=status.HTTP_404_NOT_FOUND)
    
    services = Service.objects.filter(provider=service_provider)
    orders = Order.objects.filter(service_id__in=[service.service_id for service in services])
    
    # Manually construct the response data
    response_data = []
    for order in orders:
        response_data.append({
            'order_id': order.order_id,
            'owner_name': order.owner.owner_name,  # Explicitly fetch owner's name
            'service_id': order.service_id,
            'service_name': order.service_name,
            'scheduled_date_time': order.scheduled_date_time,
            'service_provider_name': order.service_provider_name,
            'service_charges': order.service_charges,
            'status': order.status
        })

    return Response(response_data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    service_provider = ServiceProvider.objects.get(id=request.user.id)
    if order.service_id not in [service.service_id for service in Service.objects.filter(provider=service_provider)]:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    data = JSONParser().parse(request)
    serializer = OrderStatusUpdateSerializer(order, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


###########################################################

#deals function
@csrf_exempt
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_service_special(request, service_id):
    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        return Response({'error': 'User is not a service provider'}, status=status.HTTP_403_FORBIDDEN)

    service = get_object_or_404(Service, service_id=service_id)

    if service.provider != provider:
        return Response({"error": "You do not have permission to mark this service as special"}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    serializer = ServiceSerializer(service, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_service_deal(request, service_id):
    # Log the logged-in user
    print("Logged-in user:", request.user)

    # Get the logged-in user's provider profile
    try:
        provider = request.user.serviceprovider
        print("Provider object:", provider)
    except ServiceProvider.DoesNotExist:
        return Response({'error': 'User is not a service provider'}, status=status.HTTP_403_FORBIDDEN)

    # Get the service or return 404 if not found
    service = get_object_or_404(Service, service_id=service_id)
    print("Service object:", service)
    
    # Check if the service belongs to the logged-in provider
    if service.provider != provider:
        return Response({"error": "You do not have permission to mark this service as special"}, status=status.HTTP_403_FORBIDDEN)

    # Update the service with the data provided in the request
    data = request.data
    print("Request data:", data)  # Log the request data
    serializer = ServiceSerializer(service, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        print("Serializer errors:", serializer.errors)  # Log serializer errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_deal_of_the_day_services(request):
    services = Service.objects.filter(is_deal_of_the_day=True)
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_todays_special_services(request):
    services = Service.objects.filter(is_todays_special=True)
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
