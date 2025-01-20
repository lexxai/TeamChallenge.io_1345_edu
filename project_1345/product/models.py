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
            if self.property:
                property_items = self.property.items()
                if not property_items:
                    raise ValidationError("No properties provided.")
                for key, value in property_items:
                    expected_type = category_schema.get_property_type(key)
                    if expected_type:
                        # Check if the value type matches the expected type
                        if expected_type == "str" and not isinstance(value, str):
                            raise ValidationError(
                                f"Property '{key}' must be of type 'str'."
                            )
                        elif expected_type == "int" and not isinstance(value, int):
                            raise ValidationError(
                                f"Property '{key}' must be of type 'int'."
                            )
                        elif expected_type == "float" and not isinstance(value, float):
                            raise ValidationError(
                                f"Property '{key}' must be of type 'float'."
                            )
                        elif expected_type == "bool" and not isinstance(value, bool):
                            raise ValidationError(
                                f"Property '{key}' must be of type 'bool'."
                            )
                    else:
                        raise ValidationError(
                            f"Property '{key}' is not defined in the schema."
                        )

            # Check for required properties (if your schema defines required properties)
            required_properties = [
                key
                for key, prop in category_schema.schema.items()
                if isinstance(prop, dict) and prop.get("required", False)
            ]
            for req_property in required_properties:
                if (req_property and not self.property) or (
                    req_property not in self.property
                ):
                    raise ValidationError(
                        {
                            req_property: f"Property '{req_property}' is required but not provided."
                        }
                    )

        super(Product, self).save(*args, **kwargs)

    def __repr__(self):
        return '<Product object ({}) "{}">'.format(self.id, self.name)

    def __str__(self):
        return self.name
