import logging

from django.apps import apps

# from django.utils.translation import gettext_lazy as _
from django.utils.functional import LazyObject

# from django.conf import settings


logger = logging.getLogger(__name__)


class LazyLanguages(LazyObject):
    # def __init__(self, lang: list = None):
    #     super().__init__()
    #     self.lang = lang
    lang = None

    def _setup(self):
        try:
            _lang = [] if self.lang is None else self.lang
            Language = apps.get_model("language", "Language")
            if not Language:
                return []
            languages = Language.objects.filter(is_active=True).order_by("-code")
            print(languages)
            language_list = []

            lang_exist_list = [l[0] for l in _lang]

            for lang in languages:
                if lang.code not in lang_exist_list:
                    language_list.append((lang.code, lang.name))
            language_list = _lang.extend(language_list) if _lang else language_list
        except LookupError:
            language_list = (("en", "English"),)  # Default fallback

        self._wrapped = language_list


def _get_language_settings(lang: list = None) -> list[tuple[str, str]]:
    try:
        Language = apps.get_model("language", "Language")
        if not Language:
            return []
        languages = Language.objects.filter(is_active=True).order_by("-code")
        print(languages)
        language_list = []

        lang_exist_list = [l[0] for l in lang] if lang else []

        for lang in languages:
            if lang.code not in lang_exist_list:
                language_list.append((lang.code, lang.name))

        return language_list

    except LookupError:  # handle if app not ready.
        return []


PRIMARY_LANGUAGE = ("uk", "Ukrainian")
# get_language_settings = LazyLanguages()


def get_language_settings(lang: list = None):
    return LazyLanguages()


def get_request_language(request):
    lang = (
        request.headers.get("Accept-Language", "en").strip().lower()[:6].split("-")[0]
    )
    return lang


def get_not_primary_language(request, primary_lang=None) -> str | None:
    lang = get_request_language(request)
    primary_lang = primary_lang or PRIMARY_LANGUAGE[0]
    logger.debug(
        "Requested language: {}, Primary language: {}".format(lang, primary_lang)
    )
    return "en"
    # return None if primary_lang == lang else lang
