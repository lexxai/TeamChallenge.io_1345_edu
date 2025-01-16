from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CategorySchema(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    properties = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return f"Schema for {self.category.name}"

    def get_property_type(self, property_name):
        """Retrieve the type of a property."""
        return self.properties.get(property_name, {}).get("type", None)


# {
#     "color": {
#         "type": "str"
#     },
#     "size": {
#         "type": "int"
#     }
# }
