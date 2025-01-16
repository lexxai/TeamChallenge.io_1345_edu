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
    schema = models.JSONField()
