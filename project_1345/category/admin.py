from django.contrib import admin
from django.utils.translation import gettext_lazy as _


from language.models import CategoryTranslation, CategorySchemaTranslation
from .models import Category, CategorySchema


class CategoryTranslationInline(admin.TabularInline):
    model = CategoryTranslation
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "parent",
        "active",
        "display_schema_properties",
    )  # Add the custom method to the list view
    list_filter = ("active",)  # Filter by active status
    search_fields = ("name",)  # Add search functionality
    ordering = ("name",)  # Order by name
    list_editable = ("active",)  # Allow toggling active status in the list view
    inlines = [CategoryTranslationInline]

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def display_schema_properties(self, obj):
        # Fetch the CategorySchema for the current category
        category_schema = CategorySchema.objects.filter(category=obj).first()

        if category_schema:
            # Extract the properties from the schema JSON
            schema = category_schema.schema
            # Get only the names of the properties
            property_names = [key for key in schema.keys()]
            return str(property_names) if property_names else _("No properties defined")
        return _("No schema")

    display_schema_properties.short_description = _(
        "Schema Properties"
    )  # Label for the column in admin


class CategorySchemaTranslationInline(admin.TabularInline):
    model = CategorySchemaTranslation
    extra = 1


@admin.register(CategorySchema)
class CategorySchemaAdmin(admin.ModelAdmin):
    list_display = ("category", "display_properties")  # Show properties in list view
    search_fields = ("category__name",)  # Search by category name
    inlines = [CategorySchemaTranslationInline]

    def display_properties(self, obj):
        # Extract the properties from the schema JSON
        # Get only the names of the properties
        property_names = [key for key in obj.schema.keys()]
        return str(property_names) if property_names else _("No properties defined")

    display_properties.short_description = _(
        "Schema Properties"
    )  # Custom label for the column

    class Meta:
        verbose_name = _("Category Schema")
        verbose_name_plural = _("Categories Schema")
