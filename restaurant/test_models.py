from django.test import TestCase
from restaurant.models import Category, MenuItem

class CategoryModelTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(slug="pasta", title="Pasta")
        self.assertEqual(str(category.title), "Pasta")

class MenuItemModelTest(TestCase):
    def test_menu_item_creation(self):
        category = Category.objects.create(slug="drinks", title="Drinks")
        item = MenuItem.objects.create(title="Lemonade", price=3.50, featured=True, category=category)
        self.assertEqual(str(item.title), "Lemonade")
        self.assertEqual(item.category.title, "Drinks")
