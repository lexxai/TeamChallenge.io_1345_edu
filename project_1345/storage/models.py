from django.db import models

from project_1345.product.models import Product


# Create your models here.
class Storage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    date_added = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return (
            f"{self.quantity} {self.product.name}"
            if self.quantity > 1
            else self.product.name
        )

    def __repr__(self):
        return str(self)
