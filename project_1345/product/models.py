from django.db import models

from category.models import Category


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    property = models.JSONField()
    date_added = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
