from django.contrib import admin
from django.contrib.auth.models import Group
# Register your models here.
from .models import Menu, Category, MenuItem, Cart, Order, OrderItem
from .models import Booking


admin.site.register(Menu)
admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)