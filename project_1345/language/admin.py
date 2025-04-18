from django.contrib import admin

from language.models import Language


# Register your models here.
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code")
    search_fields = ("name", "code")
    list_filter = ("is_active",)


admin.site.register(Language, LanguageAdmin)
