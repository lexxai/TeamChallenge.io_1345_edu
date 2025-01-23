from pathlib import Path

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from product.models import ProductImage


# @receiver(pre_save, sender=ProductImage)
# def cache_old_image(sender, instance, **kwargs):
#     if instance.pk:
#         try:
#             instance._old_image = sender.objects.get(pk=instance.pk).image
#         except sender.DoesNotExist:
#             instance._old_image = None


# @receiver(post_save, sender=ProductImage)
# def update_image_file(sender, instance, created, **kwargs):
#     if not created:
#         old_image = getattr(instance, "_old_image", None)
#         new_image = instance.image
#         # print(old_image, new_image)
#         if old_image and old_image != new_image:
#             try:
#                 old_image_path = Path(old_image.path)
#                 if old_image_path.exists():
#                     old_image_path.unlink()  # Delete the old file
#             except ValueError:
#                 ...  # Handle invalid paths
#


@receiver(post_delete, sender=ProductImage)
def delete_image_file(sender, instance, **kwargs):
    if instance.image:
        try:
            # Attempt to use the full path directly
            image_path = Path(instance.image.path)
            if image_path.exists():
                image_path.unlink()
                return
        except ValueError:
            # `instance.image.path` may raise a ValueError if the file doesn't exist
            ...
