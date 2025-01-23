from django.db import models
from django.core.cache import cache


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the category")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, help_text="Parent category. Null if it's a root category")
    active = models.BooleanField(default=True, help_text="Is the category active?")

    def __repr__(self):
        return str(self)
        # return self.name

    def __str__(self):
        return self.get_full_path()

    def get_cache_key(self):
        return f"category_{self.id}"  # Unique cache key based on category ID

    def clear_cache(self):
        cache.delete(self.get_cache_key())

    def get_full_path(self):
        """
        Recursively build the full path of categories with parents.
        Example: 'cat-1/cat-1-1'
        """
        cache_key = self.get_cache_key()
        full_path = cache.get(cache_key)
        if not full_path:
            if self.parent:
                full_path = f"{self.parent.get_full_path()}/{self.name}"
            else:
                full_path = self.name
            cache.set(cache_key, full_path, 3600)  # Cache for 1 hour
        return full_path

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.clear_cache()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.clear_cache()


class CategorySchema(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE
    )  # Link to the Category model
    schema = models.JSONField(
        null=True, blank=True, default=dict, help_text="JSON representation of the schema. Example: {'color': {'type': 'str', 'required': true}, 'size': {'type': 'int'}}"
    )  # Store the schema as a JSON object

    class Meta:
        verbose_name = "Category Schema"
        verbose_name_plural = "Category Schemas"

    def __str__(self):
        return f"Schema for {self.category.get_full_path()}"  # Return category name for easier identification

    def __repr__(self):
        return str(self)

    def get_property_type(self, property_name):
        """Retrieve the type of a property."""
        return self.schema.get(property_name, {}).get("type", None)


# schema field:
# {
#     "color": {
#         "type": "str",
#         "required": true
#     },
#     "size": {
#         "type": "int"
#     }
# }
