# from django_json_widget.widgets import JSONEditorWidget
from django import forms
from django.contrib import admin, messages
from django.core.exceptions import FieldError, ValidationError
from django.forms import model_to_dict
from django.utils.translation import gettext_lazy as _

from .models import Product, ProductImage
from .serializers import ProductSerializer


# class ProductAdminForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = "__all__"
#         widgets = {
#             "property": JSONEditorWidget(),  # Use JSON editor for the property field
#         }


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0  # Number of empty forms displayed (1 in this case)
    fields = ("title", "image", "id")  # Fields to show for each image
    # readonly_fields = ("image",)  # Make the image field read-only if needed


class HasImagesFilter(admin.SimpleListFilter):
    title = _("has images")  # Displayed title in the filter dropdown
    parameter_name = "has_images"  # Query parameter used in the URL

    def lookups(self, request, model_admin):
        """
        Define the options for the filter (displayed in the dropdown).
        """
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        """
        Filter the queryset based on the selected value.
        """
        if self.value() == "yes":
            return queryset.filter(images__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(images__isnull=True).distinct()
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "price",
        "category",
        "active",
        "created_at",
        "updated_at",
    )
    list_editable = ("active",)
    search_fields = ("name", "owner", "category__name")  # Add search functionality
    list_filter = (
        "active",
        "category",
        "created_at",
        "updated_at",
        HasImagesFilter,
    )  # Add filters for quick filtering
    ordering = ("-created_at",)  # Default ordering in the admin
    readonly_fields = ("id", "created_at", "updated_at")  # Make timestamps read-only
    inlines = [ProductImageInline]

    def save_model1(self, request, obj, form, change):
        try:
            # Attempt to save the model instance
            obj.save()
        except FieldError as e:
            # Handle validation errors and show them in the admin interface
            # messages.get_messages(request).used = True
            self.message_user(request, f"Error saving Product: {e}", level="error")
            # raise e  # Re-raise the error so the object isn't saved

    def save_model(self, request, obj, form, change):
        # Clear any previously shown messages
        messages.get_messages(request).used = True

        # Convert the model instance to a dictionary to pass to the serializer
        data = model_to_dict(obj)

        # Serialize the model data for validation
        serializer = ProductSerializer(data=data)

        # Check if the serializer is valid
        if serializer.is_valid():
            try:
                # Save the object if the data is valid
                obj.save()
            except Exception as e:
                # Catch any errors during saving and display them
                self.message_user(request, f"Error saving Product: {e}", level="error")
        else:
            # If the serializer is not valid, show the errors
            error_messages = "\n".join(
                [
                    f"{field}: {', '.join(errors)}"
                    for field, errors in serializer.errors.items()
                ]
            )
            self.message_user(
                request, f"Validation error(s):\n{error_messages}", level="error"
            )
            # raise ValidationError("Validation failed, object not saved.")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "image",
        "product",
    )
    readonly_fields = (
        "width",
        "height",
    )
