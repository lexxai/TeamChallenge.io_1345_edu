from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "product"

    def ready(self):
        import product.signals  # Import signals here
