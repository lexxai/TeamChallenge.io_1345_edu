import uuid
from pathlib import Path

from PIL import Image
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.core.exceptions import ValidationError, FieldError
from django.db import models, connection
from django.db.models import Q
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _


from category.models import Category, CategorySchema


# Create your models here.
class Product(models.Model):
    name = models.CharField(
        max_length=255, verbose_name=_("Name"), help_text=_("Name of the product")
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Description of the product"),
    )
    sku = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("SKU"),
        help_text=_("Stock Keeping Unit of the product"),
    )  # Stock Keeping Unit
    owner = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Owner"),
        help_text=_("Owner of the product"),
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Price"),
        help_text=_("Price of the product, format: 0.00"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=_("Category"),
        help_text=_("Category of the product"),
    )
    property = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        verbose_name=_("Property"),
        help_text=format_lazy(
            "{}. Example: {{'color': 'red', 'size': 34}}", _("Property of the product")
        ),
    )
    created_at = models.DateField(
        auto_now_add=True, verbose_name=_("Created"), help_text=_("Creation date")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated"),
        help_text=_("Last updated date and time"),
    )
    active = models.BooleanField(
        default=True, verbose_name=_("Active"), help_text=_("Is the product active?")
    )

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

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
        return f"[{self.id}] {self.name}"


def generate_upload_to(instance, filename):
    # Generate a unique UUID for the file name
    filename = Path(filename)
    new_filename = str(uuid.uuid4())
    level1_folder = new_filename[:2]
    level2_folder = new_filename[2:4]
    return f"{settings.PRODUCT_IMAGE_FOLDER}/{level1_folder}/{level2_folder}/{new_filename}{filename.suffix}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to=generate_upload_to)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def pre_save(self, *args, **kwargs):
        self.prepare_previous_image()
        self.fill_image_properties()

    def post_save(self, *args, **kwargs):
        self.remove_previous_image()

    def remove_previous_image(self):
        if self.old_image and (not self.image or self.old_image != self.image):
            try:
                old_image_path = Path(self.old_image.path)
                if old_image_path.exists():
                    old_image_path.unlink()  # Delete the old file
            except ValueError:
                ...  # Handle invalid paths

    def prepare_previous_image(self):
        if self.pk:  # Only fetch old data for existing objects
            old_self = ProductImage.objects.filter(pk=self.pk).first()
            self.old_image = old_self.image if old_self else None
        else:
            self.old_image = None

    def fill_image_properties(self):
        if self.image:
            # Open the image file for reading wxh
            self.width, self.height = self.image.width, self.image.height

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)
        self.post_save()

    def __str__(self):
        return self.product.name

    def __repr__(self):
        return '<ProductImage object ({}) "{}">'.format(self.id, self.product.name)

    class Meta:
        unique_together = ("product", "image")
        indexes = [
            models.Index(fields=["product"]),
        ]
