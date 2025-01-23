from pathlib import Path

from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

from product.models import ProductImage


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

        # Fallback: Construct the path from MEDIA_ROOT and relative path
        relative_path = instance.image.name  # e.g., "product_images/image.jpg"
        if relative_path:  # Ensure relative path is not empty
            full_path = Path(settings.MEDIA_ROOT) / relative_path
            if full_path.exists():
                full_path.unlink()
