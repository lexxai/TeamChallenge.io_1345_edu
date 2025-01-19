from pydoc import describe

from django.core.management.base import BaseCommand
from category.models import Category, CategorySchema
from product.models import Product


class Command(BaseCommand):
    help = "Populate the database with base values for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",  # This makes the argument a flag (no value required)
            help="Delete all existing products and categories before populating",
        )

    def handle(self, *args, **options):
        if options.get("reset"):
            Category.objects.all().delete()
            CategorySchema.objects.all().delete()
            Product.objects.all().delete()
            self.stdout.write("Database reset.")
        self.add_categories()
        self.add_products()

    def add_categories(self):
        # Example data to populate
        categories = [
            {"name": "Electronics", "parent": None, "active": True},
            {"name": "Home Appliances", "parent": None, "active": True},
            {"name": "Mobile Phones", "parent": "Electronics", "active": True},
            {"name": "Books", "parent": None, "active": True},
            {"name": "Clothing", "parent": None, "active": True},
        ]
        schemas = [
            {"category": "Electronics", "schema": {"brand": {"type": "str"}}},
            {"category": "Mobile Phones", "schema": {"brand": {"type": "str"}}},
            {"category": "Home Appliances", "schema": {"power": {"type": "int"}}},
            {"category": "Clothing", "schema": {"size": {"type": "str"}}},
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

    def add_products(self):
        # Define products
        products = [
            {
                "name": "S21",
                "description": "Samsung Galaxy S21",
                "price": 599.99,
                "category": "Mobile Phones",
                "property": {"brand": "Samsung"},
            },
            {
                "name": "Laptop 15",
                "description": "Dell Inspiron 15",
                "price": 1299.99,
                "category": "Electronics",
                "property": {"brand": "Dell"},
            },
            {
                "name": "Novel",
                "description": "Novel science",
                "price": 14.99,
                "category": "Books",
            },
            {
                "name": "T-shirt 1",
                "description": "Basic T-shirt",
                "price": 9.99,
                "category": "Clothing",
                "property": {"size": "XL"},
            },
            {
                "name": "T-shirt 2",
                "description": "Basic T-shirt",
                "price": 19.99,
                "category": "Clothing",
                "property": {"size": "XL"},
            },
            {
                "name": "T-shirt 3",
                "description": "Basic T-shirt",
                "price": 39.99,
                "category": "Clothing",
                "property": {"size": "XXL"},
            },
            {
                "name": "T-shirt 4",
                "description": "Basic T-shirt",
                "price": 49.99,
                "category": "Clothing",
                "property": {"size": "XXL"},
            },
        ]
        # Add products to the database
        self.stdout.write("Adding products...")
        for product_data in products:
            try:
                category = Category.objects.get(name=product_data["category"])
                product, created = Product.objects.get_or_create(
                    name=product_data["name"],
                    defaults={
                        "price": product_data["price"],
                        "description": product_data["description"],
                        "category": category,
                        "property": product_data.get("property", {}),
                    },
                )
                if created:
                    self.stdout.write(f"Created product: {product.name}")
                else:
                    self.stdout.write(f"Product already exists: {product.name}")
            except Category.DoesNotExist:
                self.stdout.write(
                    f"Category not found for product: {product_data['name']}"
                )
