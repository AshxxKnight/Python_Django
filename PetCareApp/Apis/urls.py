from django.urls import path
from .Views.Owner_views import add_review, add_service_to_favorites, cancel_order, delete_favorite, list_cart_items, list_favorite_items, owner_profile, place_order, search_orders, update_owner_profile, register_owner, login_view, view_all_orders, view_order_status
from .Views.Provider_views import get_deal_of_the_day_services, get_todays_special_services, list_services_for_provider, mark_service_deal, mark_service_special, provider_profile, provider_login_view, create_service, update_order_status, update_provider_profile,update_service,register_provider,list_services,get_service,delete_service, view_orders
from .Views.Owner_views import add_service_to_cart, delete_service_from_cart, update_scheduled_time

urlpatterns = [

    # Pet Owner
    path('owner_profile-view/', owner_profile, name='owner-profile'),
    path('owner_register/', register_owner, name='register-owner'),
    path('owner_profile/update/', update_owner_profile, name='update-owner-profile'),
    path('owner_login/', login_view, name='login'),

    # Cart
    path('add_service_to_cart/', add_service_to_cart, name='add_service_to_cart'),
    path('cart_items/', list_cart_items, name='list_cart_items'),
    path('delete_service_from_cart/<int:cart_id>/', delete_service_from_cart, name='delete_service_from_cart'),
    path('update_scheduled_time/<int:cart_id>/', update_scheduled_time, name='update_scheduled_time'),

    # Order
    path('place_order/', place_order, name='place_order'),
    path('view_order_status/<int:order_id>/', view_order_status, name='view_order_status'),
    path('cancel_order/<int:order_id>/', cancel_order, name='cancel_order'),
    path('search_orders/', search_orders, name='search_orders'),
    path('view_all_orders/', view_all_orders, name='view_all_orders'),

    #Review
    path('add_review/<int:service_id>/', add_review, name='add_review'),

    #Favorite
    path('favorites/add/', add_service_to_favorites, name='add_service_to_favorites'),
    path('favorites/', list_favorite_items, name='list_favorite_items'),
     path('favorites/delete/<int:favorite_id>/', delete_favorite, name='delete_favorite'),


    ##################

    # Service Provider
    path('provider_profile/', provider_profile, name='provider_profile'),
    path('provider_profile/update/', update_provider_profile, name='update_provider_profile'),
    path('provider_register/', register_provider, name='register_provider'),
    path('provider_login/', provider_login_view, name='provider_login'),
    
    # Service
    path('create_service', create_service, name='create_service'),
    path('services/all', list_services, name='list_services'),
    path('services/one', list_services_for_provider, name='list_services_for_provider'),
    path('services/<int:service_id>', get_service, name='get_service'),
    path('services/<int:service_id>/update', update_service, name='update_service'),
    path('services/<int:service_id>/delete', delete_service, name='delete_service'),

    #Orders
    path('view_orders/', view_orders, name='view_orders'),
    path('update_order_status/<int:order_id>/', update_order_status, name='update_order_status'),

    #Deal
    path('services/<int:service_id>/mark_special/', mark_service_special, name='mark_service_special'),
    path('services/<int:service_id>/mark_deal/', mark_service_deal, name='mark_service_deal'),
    path('services/deal_of_the_day/', get_deal_of_the_day_services, name='get_deal_of_the_day_services'),
    path('services/todays_special/', get_todays_special_services, name='get_todays_special_services'),


]
