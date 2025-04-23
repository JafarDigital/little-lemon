from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from restaurant.models import Category, MenuItem

class MenuItemsViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(slug="greek", title="Greek")
        self.menu_item = MenuItem.objects.create(title="Gyro", price=7.99, featured=False, category=self.category)

    def test_get_menu_items_unauthenticated(self):
        response = self.client.get(reverse('menu-items'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_menu_items_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('menu-items'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Gyro")
