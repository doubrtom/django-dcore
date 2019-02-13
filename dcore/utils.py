import re
import unicodedata
from typing import Sequence

from django.utils.translation import gettext as _


def form_bool_choices():
    """Return tuple with yes/no choices in format for django forms.

    Returns:
        tuple.
    """
    return (
        (True, _('general.yes')),
        (False, _('general.no'))
    )


def list_to_choices(a_list: Sequence, trans_prefix: str = None, attr: str = None):
    """Convert list (sequence) into format suitable for django forms.

    If there is trans_prefix, visible values will be translated.

    Args:
        a_list (Sequence): Sequence to convert.
        trans_prefix (str): Prefix for each item in list, when set then item is translated.
        attr (str): Get attr from each item in a_list, if set.

    Returns:
        list.
    """
    choices = []
    for item in a_list:
        if attr is not None:
            val = getattr(item, attr)
        else:
            val = item
        choices.append((
            val,
            _('{}.{}'.format(trans_prefix, val)) if trans_prefix else val
        ))
    return choices


def remove_accent(text: str) -> str:
    """Remove accent from string"""
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')


def normalize_str(text: str) -> str:
    """Normalize str: Remove accent and white spaces from string and convert it into lower case."""
    text = re.sub(r'\s+', '', text)
    text = text.lower()
    return remove_accent(text)


def update_instance(instance, data: dict, properties=None):
    """Update instance properties by data from dict.

    Optionally update only properties noted in properties list.
    """
    for k, v in data.items():
        if properties and k not in properties:
            continue
        setattr(instance, k, v)
