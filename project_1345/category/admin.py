from django.contrib import admin
from .models import Category, CategorySchema


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "active")  # Fields to show in the admin list view
    list_filter = ("active",)  # Filter by active status
    search_fields = ("name",)  # Add search functionality
    ordering = ("name",)  # Order by name
    list_editable = ("active",)  # Allow toggling active status in the list view


@admin.register(CategorySchema)
class CategorySchemaAdmin(admin.ModelAdmin):
    list_display = ("category",)  # Show associated category in the list view
    search_fields = ("category__name",)  # Search by category name
