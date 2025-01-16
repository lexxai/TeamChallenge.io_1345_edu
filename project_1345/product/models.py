from django.core.exceptions import ValidationError
from django.db import models

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

    def save(self, *args, **kwargs):
        # Get the CategorySchema for the category
        category_schema = CategorySchema.objects.filter(category=self.category).first()
        if category_schema:
            # Enforce property types based on the CategorySchema
            for key, value in self.property.items():
                expected_type = category_schema.get_property_type(key)
                if expected_type:
                    if expected_type == "str" and not isinstance(value, str):
                        raise ValidationError(
                            f"Property '{key}' must be of type 'str'."
                        )
                    elif expected_type == "int" and not isinstance(value, int):
                        raise ValidationError(
                            f"Property '{key}' must be of type 'int'."
                        )
                    # Add more types (e.g., float, bool) as needed

        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
