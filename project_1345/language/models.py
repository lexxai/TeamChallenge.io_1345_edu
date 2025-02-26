from django.db import models

from product.models import Product


class Language(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ProductTranslation(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="translations"
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, help_text="Name of the product")
    description = models.TextField(
        null=True, blank=True, help_text="Description of the product"
    )

    class Meta:
        unique_together = ("product", "language")

    def __str__(self):
        return f"{self.product.id} - {self.language.code} Translation"
