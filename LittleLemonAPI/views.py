from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission, SAFE_METHODS, IsAdminUser
from rest_framework.generics import ListCreateAPIView
from django.contrib.auth.models import User, Group
from .models import MenuItem, Cart, Order, OrderItem, Category
from .serializers import *
from datetime import date
from .permissions import IsManager, IsDeliveryCrew, IsCustomer
from django.shortcuts import get_object_or_404
from .permissions import IsManagerOrAdmin

class IsManagerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.groups.filter(name='Manager').exists()

# Menu Items

class MenuItemsView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]

    def get(self, request: Request):
        items = MenuItem.objects.all()

        # Filtering
        category = request.query_params.get('category')
        if category:
            items = items.filter(category=category)

        # Ordering
        ordering = request.query_params.get('ordering')
        if ordering:
            items = items.order_by(ordering)

        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data)

        # ✅ Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 5
        result_page = paginator.paginate_queryset(items, request)
        serializer = MenuItemSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = MenuItemCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

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

# Categories

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Manager').exists()

class CategoryListCreateView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManagerOrAdmin()]
        return [IsAuthenticated()]


# Cart

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CartSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({'message': 'Cart cleared.'}, status=204)

# Orders

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
            return Response({'detail': 'Cart is empty.'}, status=400)

        total = sum([item.price for item in cart_items])
        order = Order.objects.create(
            user=request.user,
            total=total,
            date=date.today()
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )
        cart_items.delete()
        return Response({'message': 'Order placed successfully.'}, status=201)

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        user = request.user
        if order.user != user and not user.groups.filter(name__in=['Manager', 'Delivery crew']).exists():
            return Response({'detail': 'Forbidden'}, status=403)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.groups.filter(name='Manager').exists():
            return Response({'detail': 'Only managers can update orders.'}, status=403)

        order = get_object_or_404(Order, pk=pk)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        # Check if user is Manager
        if request.user.groups.filter(name='Manager').exists():
            serializer = OrderSerializer(order, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        # Check if user is Delivery Crew
        elif request.user.groups.filter(name='Delivery crew').exists():
            if order.delivery_crew != request.user:
                return Response({'detail': 'Forbidden: not your assigned order.'}, status=403)

            # Allow only status update
            status_value = request.data.get('status')
            if status_value is None:
                return Response({'detail': 'Missing status field.'}, status=400)

            order.status = status_value
            order.save()
            return Response({'message': 'Order status updated.'}, status=200)

        # Everyone else – deny
        return Response({'detail': 'Only managers or assigned delivery crew can update.'}, status=403)

    def delete(self, request, pk):
        if not request.user.groups.filter(name='Manager').exists():
            return Response({'detail': 'Only managers can delete orders.'}, status=403)

        order = get_object_or_404(Order, pk=pk)
        order.delete()
        return Response(status=204)

# Group Management

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
