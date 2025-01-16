# from django_json_widget.widgets import JSONEditorWidget
from django import forms
from django.contrib import admin
from .models import Product


# class ProductAdminForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = "__all__"
#         widgets = {
#             "property": JSONEditorWidget(),  # Use JSON editor for the property field
#         }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
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
    )  # Add filters for quick filtering
    ordering = ("-created_at",)  # Default ordering in the admin
    readonly_fields = ("created_at", "updated_at")  # Make timestamps read-only
