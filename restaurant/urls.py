from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    MenuItemsView, SingleMenuItemView,
    CartView, OrderListCreateView, OrderDetailView,
    CategoryListCreateView,
    UserListView,
    ManagerUsersView, SingleManagerUserView,
    DeliveryCrewUsersView, SingleDeliveryCrewUserView,
    signup_view,
)

urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('book/', views.book, name="book"),
    path('reservations/', views.reservations, name="reservations"),

    path('menu/', views.menu_view, name='menu'),
    path('menu_item/<int:pk>/', views.display_menu_item, name="menu_item"),

    path('bookings', views.bookings, name='bookings'),

    path('token/login/', obtain_auth_token, name='api_token_auth'),

    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='menu'), name='logout'),
    path('signup/', signup_view, name='signup'),

    path('menu-items/', MenuItemsView.as_view(), name='menu-items'),
    path('menu-items/<int:pk>/', SingleMenuItemView.as_view(), name='single-menu-item'),

    path('categories/', CategoryListCreateView.as_view(), name='categories'),

    path('cart/menu-items/', CartView.as_view(), name='cart'),

    path('orders/', OrderListCreateView.as_view(), name='orders'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),

    path('users/', UserListView.as_view(), name='users'),

    path('groups/manager/users', ManagerUsersView.as_view(), name='manager-users'),
    path('groups/manager/users/<int:userId>/', SingleManagerUserView.as_view(), name='single-manager'),

    path('groups/delivery-crew/users', DeliveryCrewUsersView.as_view(), name='delivery-crew-users'),
    path('groups/delivery-crew/users/<int:userId>/', SingleDeliveryCrewUserView.as_view(), name='single-delivery-crew'),

    # DRF API Views - included from previous assignment
    path('api/menu-items/', views.MenuItemsView.as_view(), name='menu_items'),
    path('api/menu-items/<int:pk>/', views.SingleMenuItemView.as_view(), name='menu_item_detail'),

    path('api/categories/', views.CategoryListCreateView.as_view(), name='categories'),

    path('api/cart/menu-items/', views.CartView.as_view(), name='cart'),
    path('api/orders/', views.OrderListCreateView.as_view(), name='orders'),
    path('api/orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),

    path('api/groups/manager/users/', views.ManagerUsersView.as_view(), name='manager_users'),
    path('api/groups/manager/users/<int:userId>/', views.SingleManagerUserView.as_view(), name='single_manager_user'),

    path('api/groups/delivery-crew/users/', views.DeliveryCrewUsersView.as_view(), name='delivery_users'),
    path('api/groups/delivery-crew/users/<int:userId>/', views.SingleDeliveryCrewUserView.as_view(), name='single_delivery_user'),

    path('api/users/', views.UserListView.as_view(), name='user_list'),
]