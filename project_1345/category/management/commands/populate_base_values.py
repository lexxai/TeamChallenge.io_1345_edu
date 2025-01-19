from django.core.management.base import BaseCommand
from category.models import Category, CategorySchema


class Command(BaseCommand):
    help = "Populate the database with base values for development"

    def handle(self, *args, **kwargs):
        # Example data to populate
        categories = [
            {"name": "Electronics", "parent": None, "active": True},
            {"name": "Home Appliances", "parent": None, "active": True},
            {"name": "Mobile Phones", "parent": "Electronics", "active": True},
        ]
        schemas = [
            {"category": "Electronics", "schema": {"brand": {"type": "str"}}},
            {"category": "Home Appliances", "schema": {"power": {"type": "int"}}},
        ]

        # Add categories
        for cat_data in categories:
            parent_name = cat_data.pop("parent")
            parent = (
                Category.objects.filter(name=parent_name).first()
                if parent_name
                else None
            )
            cat_data["parent"] = parent
            category, created = Category.objects.get_or_create(**cat_data)
            self.stdout.write(
                f"{'Created' if created else 'Updated'} Category: {category.name}"
            )

        # Add schemas
        for schema_data in schemas:
            category = Category.objects.filter(name=schema_data["category"]).first()
            if not category:
                self.stdout.write(f"Category not found: {schema_data['category_name']}")
                continue
            schema, created = CategorySchema.objects.get_or_create(
                category=category, defaults={"schema": schema_data["schema"]}
            )
            self.stdout.write(
                f"{'Created' if created else 'Updated'} Schema for: {category.name}"
            )
