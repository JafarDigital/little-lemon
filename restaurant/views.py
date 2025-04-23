# from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework import status

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from .forms import BookingForm
from .models import Menu, MenuItem, Cart, Order, OrderItem, Category
from django.core import serializers
from .models import Booking, MenuItem, MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CartSerializer, OrderSerializer, MenuItemCreateUpdateSerializer, UserSerializer, CategorySerializer
from .permissions import IsManager, IsCustomer, IsManagerOrAdmin
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def reservations(request):
    date = request.GET.get('date',datetime.today().date())
    bookings = Booking.objects.all()
    booking_json = serializers.serialize('json', bookings)
    return render(request, 'bookings.html',{"bookings":booking_json})

def book(request):
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form':form}
    return render(request, 'book.html', context)

def menu(request):
    menu_data = Menu.objects.all()
    main_data = {"menu": menu_data}
    return render(request, 'menu.html', {"menu": main_data})

def menu_view(request):
    categories = Category.objects.all()
    categorized_menu = []

    for category in categories:
        items = MenuItem.objects.filter(category=category)
        categorized_menu.append((category, items))

    return render(request, 'menu.html', {'categorized_menu': categorized_menu})

def display_menu_item(request, pk=None): 
    if pk: 
        menu_item = Menu.objects.get(pk=pk) 
    else: 
        menu_item = "" 
    return render(request, 'menu_item.html', {"menu_item": menu_item})

def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('menu')  # or another page
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after signup
            return redirect('menu')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@csrf_exempt
def bookings(request):
    if request.method == 'POST':
        data = json.load(request)  # Parse JSON from request body

        # Check if booking exists for the same date and time
        exist = Booking.objects.filter(
            reservation_date=data['reservation_date']
        ).filter(
            reservation_slot=data['reservation_slot']
        ).exists()

        if not exist:
            booking = Booking(
                first_name=data['first_name'],
                reservation_date=data['reservation_date'],
                reservation_slot=data['reservation_slot']
            )
            booking.save()
        else:
            return HttpResponse(
                "{'error':1}",
                content_type='application/json'
            )

    # Handle GET requests
    date = request.GET.get('date', datetime.today().date())
    bookings = Booking.objects.filter(reservation_date=date)
    booking_json = serializers.serialize('json', bookings)

    return HttpResponse(booking_json, content_type='application/json')

# Included from previous assignments

class IsManagerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.groups.filter(name='Manager').exists()

class MenuItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = MenuItem.objects.all()
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.groups.filter(name='Manager').exists():
            return Response({'detail': 'Only managers can add items.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = MenuItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Cart API for Customers
class CartView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({'message': 'Cart cleared.'}, status=status.HTTP_204_NO_CONTENT)

# Orders API
class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.groups.filter(name='Manager').exists():
            orders = Order.objects.all()
        elif user.groups.filter(name='Delivery crew').exists():
            orders = Order.objects.filter(delivery_crew=user)
        else:
            orders = Order.objects.filter(user=user)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(item.price for item in cart_items)
        order = Order.objects.create(user=request.user, total=total)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )
        cart_items.delete()
        return Response({'message': 'Order placed successfully.'}, status=status.HTTP_201_CREATED)

class SingleMenuItemView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]

    def get(self, request, pk):
        item = get_object_or_404(MenuItem, pk=pk)
        serializer = MenuItemSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        item = get_object_or_404(MenuItem, pk=pk)
        serializer = MenuItemCreateUpdateSerializer(item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        if not request.user.groups.filter(name='Manager').exists():
            return Response({'detail': 'Forbidden'}, status=403)
        item = get_object_or_404(MenuItem, pk=pk)
        serializer = MenuItemCreateUpdateSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        item = get_object_or_404(MenuItem, pk=pk)
        item.delete()
        return Response(status=204)

# Single Order View for Manager and Delivery Crew
class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if order.user != request.user and not request.user.groups.filter(name__in=['Manager', 'Delivery crew']).exists():
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        # Manager assigns delivery crew
        if request.user.groups.filter(name='Manager').exists():
            serializer = OrderSerializer(order, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        # Delivery marks as delivered
        elif request.user.groups.filter(name='Delivery crew').exists() and 'status' in request.data:
            order.status = request.data['status']
            order.save()
            return Response({'message': 'Order updated by delivery crew.'})
        return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    class UserListView(APIView):
        permission_classes = [IsAdminUser]

        def get(self, request):
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)

    class ManagerUsersView(APIView):
        permission_classes = [IsAuthenticated, IsAdminUser]

        def get(self, request):
            managers = User.objects.filter(groups__name='Manager')
            serializer = UserSerializer(managers, many=True)
            return Response(serializer.data)

        def post(self, request):
            user = get_object_or_404(User, id=request.data['user_id'])
            group = Group.objects.get(name='Manager')
            group.user_set.add(user)
            return Response({'message': 'User added to manager group.'}, status=201)

    class SingleManagerUserView(APIView):
        permission_classes = [IsAuthenticated, IsAdminUser]

        def delete(self, request, userId):
            user = get_object_or_404(User, id=userId)
            group = Group.objects.get(name='Manager')
            group.user_set.remove(user)
            return Response({'message': 'User removed from manager group.'}, status=204)

    class DeliveryCrewUsersView(APIView):
        permission_classes = [IsAuthenticated, IsManagerOrAdmin]

        def get(self, request):
            crew = User.objects.filter(groups__name='Delivery crew')
            serializer = UserSerializer(crew, many=True)
            return Response(serializer.data)

        def post(self, request):
            user = get_object_or_404(User, id=request.data['user_id'])
            group = Group.objects.get(name='Delivery crew')
            group.user_set.add(user)
            return Response({'message': 'User added to delivery crew.'}, status=201)

    class SingleDeliveryCrewUserView(APIView):
        permission_classes = [IsAuthenticated, IsManagerOrAdmin]

        def delete(self, request, userId):
            user = get_object_or_404(User, id=userId)
            group = Group.objects.get(name='Delivery crew')
            group.user_set.remove(user)
            return Response({'message': 'User removed from delivery crew.'}, status=204)

class CategoryListCreateView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManagerOrAdmin()]
        return [IsAuthenticated()]

# List all users (admin only)
class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class ManagerUsersView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        managers = User.objects.filter(groups__name='Manager')
        serializer = UserSerializer(managers, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = get_object_or_404(User, id=request.data['user_id'])
        group = Group.objects.get(name='Manager')
        group.user_set.add(user)
        return Response({'message': 'User added to manager group.'}, status=201)

class SingleManagerUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, userId):
        user = get_object_or_404(User, id=userId)
        group = Group.objects.get(name='Manager')
        group.user_set.remove(user)
        return Response({'message': 'User removed from manager group.'}, status=204)

class DeliveryCrewUsersView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]

    def get(self, request):
        crew = User.objects.filter(groups__name='Delivery crew')
        serializer = UserSerializer(crew, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = get_object_or_404(User, id=request.data['user_id'])
        group = Group.objects.get(name='Delivery crew')
        group.user_set.add(user)
        return Response({'message': 'User added to delivery crew.'}, status=201)

class SingleDeliveryCrewUserView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]

    def delete(self, request, userId):
        user = get_object_or_404(User, id=userId)
        group = Group.objects.get(name='Delivery crew')
        group.user_set.remove(user)
        return Response({'message': 'User removed from delivery crew.'}, status=204)
