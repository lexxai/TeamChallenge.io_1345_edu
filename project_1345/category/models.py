from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CategorySchema(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE
    )  # Link to the Category model
    schema = models.JSONField(
        null=True, blank=True, default=dict
    )  # Store the schema as a JSON object

    class Meta:
        verbose_name = "Category Schema"
        verbose_name_plural = "Category Schemas"

    def __str__(self):
        return f"Schema for {self.category.name}"  # Return category name for easier identification

    def __repr__(self):
        return str(self)

    def get_property_type(self, property_name):
        """Retrieve the type of a property."""
        return self.schema.get(property_name, {}).get("type", None)


# {
#     "color": {
#         "type": "str",
#         "required": true
#     },
#     "size": {
#         "type": "int"
#     }
# }
