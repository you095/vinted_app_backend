from django.core.management.base import BaseCommand
from vinted_api.models import Condition

class Command(BaseCommand):
    help = 'Adds predefined conditions to the database'

    def handle(self, *args, **kwargs):
        conditions = [
            {
                "name": "neuf",
                "display_name": "Neuf",
                "description": "Article neuf avec étiquettes",
                "order": 1
            },
            {
                "name": "tres_bon",
                "display_name": "Très bon état",
                "description": "Article porté quelques fois, comme neuf",
                "order": 2
            },
            {
                "name": "bon",
                "display_name": "Bon état",
                "description": "Article en bon état général",
                "order": 3
            },
            {
                "name": "satisfaisant",
                "display_name": "État satisfaisant",
                "description": "Article usé mais portable",
                "order": 4
            }
        ]

        for condition_data in conditions:
            condition, created = Condition.objects.get_or_create(
                name=condition_data['name'],
                defaults={
                    'display_name': condition_data['display_name'],
                    'description': condition_data['description'],
                    'order': condition_data['order']
                }
            )
            if created:
                self.stdout.write(f"Created condition: {condition.display_name}")
            else:
                self.stdout.write(f"Condition already exists: {condition.display_name}")

        self.stdout.write(self.style.SUCCESS('Conditions added successfully!')) 