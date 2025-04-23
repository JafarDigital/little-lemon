from django.test import TestCase, Client
from django.urls import reverse
from .models import Menu, Booking
from datetime import date

class RestaurantTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.menu = Menu.objects.create(title="Pizza", price=12.50, inventory=10)

    def test_menu_item_creation(self):
        self.assertEqual(self.menu.title, "Pizza")
        self.assertEqual(float(self.menu.price), 12.50)
        self.assertEqual(self.menu.inventory, 10)

    def test_menu_list_view(self):
        response = self.client.get(reverse('menu'))  # make sure 'menu' is your URL name
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pizza")

    def test_booking_post(self):
        data = {
            "first_name": "Jafar",
            "reservation_date": "2025-04-25",
            "reservation_slot": 12
        }
        response = self.client.post(reverse('bookings'), data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), 1)

    def test_duplicate_booking_rejected(self):
        Booking.objects.create(first_name="Ali", reservation_date="2025-04-25", reservation_slot=12)
        data = {
            "first_name": "Jafar",
            "reservation_date": "2025-04-25",
            "reservation_slot": 12
        }
        response = self.client.post(reverse('bookings'), data, content_type='application/json')
        self.assertContains(response, '"error":1', status_code=200)
