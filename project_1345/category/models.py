from django.db import models
from django.core.cache import cache
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _, get_language


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, help_text=_("Name of the category"))
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_("Parent category. Null if it's a root category"),
    )
    active = models.BooleanField(default=True, help_text=_("Is the category active?"))

    def __repr__(self):
        return str(self)
        # return self.name

    def __str__(self):
        return self.get_full_path()

    def get_cache_key(self, lang=None):
        if lang is None:
            lang = get_language()  # or default to 'en'
        return f"category_{self.pk}_{lang}"

    def clear_cache(self):
        cache.delete(self.get_cache_key())

    def get_translated_name(self, lang=None):
        if hasattr(self, "preferred_translations") and self.preferred_translations:
            return self.preferred_translations[0].name or self.name
        return self.name

    def get_full_path(self, lang=None):
        """
        Recursively build the full path of categories with parents.
        Example: 'cat-1/cat-1-1' in user's language
        """
        if lang is None:
            lang = get_language()

        cache_key = self.get_cache_key(lang)
        full_path = cache.get(cache_key)

        if not full_path:
            name = self.get_translated_name(lang)
            if self.parent:
                full_path = f"{self.parent.get_full_path(lang)}/{name}"
            else:
                full_path = name
            cache.set(cache_key, full_path, 3600)  # Cache for 1 hour

        return full_path

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.clear_cache()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.clear_cache()

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class CategorySchema(models.Model):
    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        verbose_name=_("Category"),
        help_text=_("Category associated with the schema"),
        related_name="schema",
    )  # Link to the Category model
    schema = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        verbose_name=_("Schema"),
        help_text=format_lazy(
            "{}. Types: [str, int, float, bool]. "
            "{}: {{'color': {{'type': 'str', 'required': true}}, 'size': {{'type': 'int'}}}}",
            _("JSON representation of the schema"),
            _("Example"),
        ),
    )  # Store the schema as a JSON object

    class Meta:
        verbose_name = _("Category Schema")
        verbose_name_plural = _("Category Schemas")

    def __str__(self):
        return str(format_lazy("{} {}", _("Schema for"), self.category.get_full_path()))

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
