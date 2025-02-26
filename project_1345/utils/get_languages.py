# from django.apps import apps
# from django.utils.translation import gettext_lazy as _
#
#
# def get_language_settings(lang: list = None):
#     try:
#         Language = apps.get_model("language", "Language")
#         languages = Language.objects.filter(is_active=True).order_by("-code")
#         language_list = []
#
#         lang_exist_list = [l[0] for l in lang] if lang else []
#
#         for lang in languages:
#             if lang.code not in lang_exist_list:
#                 language_list.append((lang.code, lang.name))
#
#         return language_list
#
#     except LookupError:  # handle if app not ready.
#         return None, []
