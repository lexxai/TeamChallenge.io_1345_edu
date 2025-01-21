from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from django.db import connection

from product.models import Product


class Command(BaseCommand):
    help = "Populate search_vector for existing products"

    def handle(self, *args, **kwargs):
        if connection.vendor != "postgresql":
            self.stdout.write(
                self.style.ERROR(
                    "This command is only supported on PostgreSQL databases"
                )
            )
            return

        products = Product.objects.filter(search_vector__isnull=True)
        for product in products:
            product.search_vector = SearchVector("name", weight="A") + SearchVector(
                "description", weight="B"
            )
            product.save(update_fields=["search_vector"])
        self.stdout.write(
            self.style.SUCCESS(
                "Search vector populated for all not prepopulated products"
            )
        )
