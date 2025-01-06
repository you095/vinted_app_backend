import json
from django.core.management.base import BaseCommand
from vinted_api.models import Category

class Command(BaseCommand):
    help = 'Ajoute les catégories et sous-catégories dans la base de données'

    def handle(self, *args, **kwargs):
        categories = [
            {"name": "Hommes", "description": "Vêtements et accessoires pour hommes", "parent": None},
            {"name": "Femmes", "description": "Vêtements et accessoires pour femmes", "parent": None},
            {"name": "Enfants", "description": "Produits pour enfants", "parent": None},
            {"name": "Électronique", "description": "Produits électroniques", "parent": None},
            {"name": "Sports", "description": "Équipements et vêtements de sport", "parent": None},
            {"name": "Maison", "description": "Produits pour la maison", "parent": None},
            {"name": "Vêtements Hommes", "display_name": "Vêtements", "description": "Vêtements pour hommes", "parent": "Hommes"},
            {"name": "Chaussures Hommes", "display_name": "Chaussures", "description": "Chaussures pour hommes", "parent": "Hommes"},
            {"name": "Accessoires Hommes", "display_name": "Accessoires", "description": "Accessoires pour hommes", "parent": "Hommes"},
            {"name": "Vêtements Femmes", "display_name": "Vêtements", "description": "Vêtements pour femmes", "parent": "Femmes"},
            {"name": "Chaussures Femmes", "display_name": "Chaussures", "description": "Chaussures pour femmes", "parent": "Femmes"},
            {"name": "Jouets Enfants", "display_name": "Jouets", "description": "Jouets pour enfants", "parent": "Enfants"},
        ]

        # First, create all parent categories
        for category in [c for c in categories if c['parent'] is None]:
            Category.objects.get_or_create(
                name=category['name'],
                defaults={'description': category['description']}
            )
            self.stdout.write(f"Created parent category: {category['name']}")

        # Then create subcategories
        for category in [c for c in categories if c['parent'] is not None]:
            parent = Category.objects.get(name=category['parent'])
            display_name = category.get('display_name', category['name'])
            Category.objects.get_or_create(
                name=category['name'],  # Unique name
                defaults={
                    'description': category['description'],
                    'parent': parent,
                }
            )
            self.stdout.write(f"Created subcategory: {category['name']} under {parent.name}")

        self.stdout.write(self.style.SUCCESS('Catégories ajoutées avec succès !')) 