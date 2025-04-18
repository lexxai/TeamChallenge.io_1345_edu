import logging

from django.conf import settings
from django.utils.translation import get_language

logger = logging.getLogger(__name__)


def get_request_language(request):
    lang = (
        request.headers.get("Accept-Language", "en").strip().lower()[:6].split("-")[0]
    )
    return lang


def get_not_primary_language(primary_lang=None) -> str | None:
    lang = get_language()
    primary_lang = primary_lang or settings.LANGUAGE_CODE
    logger.debug(
        "Requested language: {}, Primary language: {}".format(lang, primary_lang)
    )
    # return "en"
    return None if primary_lang == lang else lang
