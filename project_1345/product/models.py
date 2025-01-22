import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.core.exceptions import ValidationError, FieldError
from django.db import models, connection
from django.db.models import Q

from category.models import Category, CategorySchema


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    owner = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    property = models.JSONField(null=True, blank=True, default=dict)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-updated_at"]

        indexes = [
            models.Index(fields=["-updated_at"]),
            models.Index(fields=["category"]),
            models.Index(fields=["name"]),
            models.Index(fields=["price"]),
            models.Index(fields=["name", "price"]),
            models.Index(fields=["category", "name", "price"]),
            models.Index(Q(active=True), name="active_products_idx"),
        ]
        # Conditionally add the field based on the database backend
        if connection.vendor == "postgresql":
            search_vector = SearchVectorField(null=True, blank=True)

        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)

            if connection.vendor == "postgresql":
                cls._meta.indexes.append(
                    GinIndex(fields=["property"])
                )  # Add GIN index dynamically for PostgreSQL only

    def save(self, *args, **kwargs):
        if connection.vendor == "postgresql":
            self.search_vector = SearchVector("name", weight="A") + SearchVector(
                "description", weight="B"
            )

        # Moved check from save of model to serialize class validate method
        # # Get the CategorySchema for the category
        # category_schema = CategorySchema.objects.filter(category=self.category).first()
        #
        # if category_schema:
        #     # Enforce property types based on the CategorySchema
        #     if self.property:
        #         property_items = self.property.items()
        #         if not property_items:
        #             raise FieldError({"property": "No properties provided."})
        #         for key, value in property_items:
        #             expected_type = category_schema.get_property_type(key)
        #             if expected_type:
        #                 # Check if the value type matches the expected type
        #                 if expected_type == "str" and not isinstance(value, str):
        #                     raise FieldError(
        #                         {key: f"Property '{key}' must be of type 'str'."}
        #                     )
        #                 elif expected_type == "int" and not isinstance(value, int):
        #                     raise FieldError(
        #                         {key: f"Property '{key}' must be of type 'int'."}
        #                     )
        #                 elif expected_type == "float" and not isinstance(value, float):
        #                     raise FieldError(
        #                         {key: f"Property '{key}' must be of type 'float'."}
        #                     )
        #                 elif expected_type == "bool" and not isinstance(value, bool):
        #                     raise FieldError(
        #                         {key: f"Property '{key}' must be of type 'bool'."}
        #                     )
        #             else:
        #                 raise FieldError(
        #                     {key: f"Property '{key}' is not defined in the schema."}
        #                 )
        #
        #     # Check for required properties (if your schema defines required properties)
        #     required_properties = [
        #         key
        #         for key, prop in category_schema.schema.items()
        #         if isinstance(prop, dict) and prop.get("required", False)
        #     ]
        #     for req_property in required_properties:
        #         if (req_property and not self.property) or (
        #             req_property not in self.property
        #         ):
        #             raise FieldError(
        #                 {
        #                     req_property: f"Property '{req_property}' is required but not provided."
        #                 }
        #             )

        super(Product, self).save(*args, **kwargs)

    def __repr__(self):
        return '<Product object ({}) "{}">'.format(self.id, self.name)

    def __str__(self):
        return self.name


def generate_upload_to(instance, filename):
    # Generate a unique UUID for the file name
    filename = Path(filename)
    return f"{settings.PRODUCT_IMAGE_FOLDER}/{uuid.uuid4()}{filename.suffix}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=generate_upload_to)

    def __str__(self):
        return self.product.name

    def __repr__(self):
        return '<ProductImage object ({}) "{}">'.format(self.id, self.product.name)

    class Meta:
        unique_together = ("product", "image")
        indexes = [
            models.Index(fields=["product"]),
        ]
