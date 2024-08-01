from django.contrib import admin

# Register your models here.
from .models.Owner_models import Owner, Order, Cart, Favorites
from .models.Provider_models import ServiceProvider, Service
from .models.Users import User


admin.site.register(Owner)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Favorites)
admin.site.register(ServiceProvider)
admin.site.register(Service)
admin.site.register(User)