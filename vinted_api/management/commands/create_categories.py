from django.core.management.base import BaseCommand
from vinted_api.models import Category

class Command(BaseCommand):
    help = 'Creates default categories and subcategories'

    def handle(self, *args, **kwargs):
        # First, clear existing categories
        Category.objects.all().delete()

        # Root categories and subcategories
        categories_data = [
            {"name": "Fashion", "subcategories": [
                "Men's Clothing", "Women's Clothing", "Accessories", "Kids' Clothing"]},
            {"name": "Electronics", "subcategories": [
                "Smartphones & Tablets", "Laptops & Computers", "Home Appliances", "Gaming"]},
            {"name": "Home & Furniture", "subcategories": [
                "Furniture", "Home Décor", "Kitchenware"]},
            {"name": "Sports & Outdoor", "subcategories": [
                "Sports Equipment", "Outdoor Equipment"]},
            {"name": "Beauty & Health", "subcategories": [
                "Makeup", "Skincare", "Hair Care"]},
            {"name": "Vehicles", "subcategories": [
                "Cars", "Motorcycles & Scooters", "Bicycles"]},
            {"name": "Books, Movies & Music", "subcategories": [
                "Books", "Movies & Series", "Music"]},
            {"name": "Toys & Games", "subcategories": [
                "Toys for Kids", "Video Games"]},
            {"name": "Art & Collectibles", "subcategories": [
                "Artwork", "Collectibles"]},
            {"name": "Miscellaneous", "subcategories": [
                "Free Items", "Services"]},
        ]

        for category_data in categories_data:
            category = Category.objects.create(name=category_data['name'])
            for subcategory_name in category_data['subcategories']:
                Category.objects.create(name=subcategory_name, parent=category)
            
            self.stdout.write(
                self.style.SUCCESS(f'Created category "{category.name}" with {len(category_data["subcategories"])} subcategories')
            ) 