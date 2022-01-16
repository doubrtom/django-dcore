from typing import Iterable, List

from django.utils.translation import gettext_lazy
from rest_framework_friendly_errors import settings


def validation_failed_items(
    items: Iterable[List]
):
    """Generate items for errors field in format of DRF-friendly-errors.

    Parameters
    ----------
    items
        Items to generate errors.
        len(item) == 3, generate dict in format {"code": i[0], "field": i[1], "message": i[2]}
        len(item) == 4, generate dict in format:
            {"code": i[0], "field": i[1], "message": i[2], "errors": validation_failed_items(i[3])}
        len(item) == 0, generate empty dict, i.e. {}


    """
    formatted_errors = []
    for item in items:
        if len(item) == 0:
            formatted_errors.append({})
        if len(item) == 3:
            formatted_errors.append({
                'code': item[0],
                'field': item[1],
                'message': item[2],
            })
        if len(item) == 4:
            formatted_errors.append({
                'code': item[0],
                'field': item[1],
                'message': item[2],
                'errors': validation_failed_items(item[3]),
            })
        return formatted_errors


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
        'errors': validation_failed_items(items),
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
