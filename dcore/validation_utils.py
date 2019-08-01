from typing import Iterable

from django.utils.translation import gettext_lazy
from rest_framework_friendly_errors import settings


def validation_failed_dict(
    items: Iterable,
    dict_code: int = 1001,
    dict_message: str = 'Validation Failed'
):
    """Generate dict for failed validation in format of DRF-friendly-errors.

    Attributes:
        items: Items to put into dict. In format: [(code, field, message), ...]

    Returns:
        dict: In format of DRF
    """
    return {
        'code': dict_code,
        'message': dict_message,
        'errors': [
            {'code': i[0], 'field': i[1], 'message': i[2]} for i in items
        ]
    }


def username_duplicated(message_trans_key: str = 'username_duplicated'):
    """Return failed validation dict for duplicated username.

    Attributes:
        message_trans_key: Error message as key used for translation function (gettext).

    Returns:
        dict: In format of DRF
    """
    item = (
        settings.FRIENDLY_VALIDATOR_ERRORS['UniqueValidator'],
        'username',
        gettext_lazy(message_trans_key)
    )
    return validation_failed_dict([item])
