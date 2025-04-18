from django.db import models
from django.utils.translation import gettext_lazy as _


from category.models import Category, CategorySchema
from product.models import Product


class Language(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")


class ProductTranslation(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="translations"
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, help_text=_("Name of the product"))
    description = models.TextField(
        null=True, blank=True, help_text=_("Description of the product")
    )

    class Meta:
        unique_together = ("product", "language")

    def __str__(self):
        return f"{self.product.id} - {self.language.code} Translation"


class CategoryTranslation(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="translations"
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, help_text=_("Name of the category"))

    class Meta:
        unique_together = ("category", "language")

    def __str__(self):
        return f"{self.category.name} - {self.language.code} Translation"


class CategorySchemaTranslation(models.Model):
    category_schema = models.ForeignKey(
        CategorySchema, on_delete=models.CASCADE, related_name="translations"
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    schema = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text="JSON representation of the schema key related to primary language of schema."
        "Example: {'color': 'колір', 'size': 'розмір'}",
    )

    class Meta:
        unique_together = ("category_schema", "language")

    def __str__(self):
        primary_schema = self.category_schema.schema
        schema_keys = ",".join(primary_schema.keys() if primary_schema else [])
        translation_label = _("Translation")
        return f"{self.category_schema.category.name} - [{schema_keys}] - {self.language.code} {translation_label}"
