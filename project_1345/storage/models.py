from django.db import models

from project_1345.product.models import Product


class Storage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Storage Entry"
        verbose_name_plural = "Storage Entries"
        ordering = ["-created_at"]  # Most recent first

    def __str__(self):
        if self.product:
            return (
                f"{self.quantity} {self.product.name}"
                if self.quantity > 1
                else self.product.name
            )
        return "Unknown Product"

    def __repr__(self):
        return str(self)
