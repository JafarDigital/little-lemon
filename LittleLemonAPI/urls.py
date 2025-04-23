from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import CategoryListCreateView, UserListView

from . import views

urlpatterns = [
    path('token/login/', obtain_auth_token),

    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view()),

    path('cart/menu-items/', views.CartView.as_view()),

    path('orders/', views.OrderListCreateView.as_view()),
    path('orders/<int:pk>/', views.OrderDetailView.as_view()),

    path('users/', UserListView.as_view()),

    path('categories/', CategoryListCreateView.as_view()),

    path('groups/manager/users/', views.ManagerUsersView.as_view()),
    path('groups/manager/users/<int:userId>/', views.SingleManagerUserView.as_view()),

    path('groups/delivery-crew/users/', views.DeliveryCrewUsersView.as_view()),
    path('groups/delivery-crew/users/<int:userId>/', views.SingleDeliveryCrewUserView.as_view()),
]
