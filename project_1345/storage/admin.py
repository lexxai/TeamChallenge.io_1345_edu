from django.contrib import admin
from .models import Storage


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity", "created_at", "updated_at", "active")
    list_editable = ("active",)
    search_fields = ("product__name",)  # Search by product name
    list_filter = ("active", "created_at")  # Filter by active status and creation date
    ordering = ("-created_at",)  # Default ordering: most recent first
    readonly_fields = (
        "created_at",
        "updated_at",
    )  # Prevent manual editing of timestamps
