from enum import Enum
from typing import Sequence

from django.utils.translation import gettext as _


class ChoiceEnum(Enum):
    """Base enum class, usable for django forms."""

    @classmethod
    def choices(cls, trans_prefix: str = None, exclude: Sequence=None):
        """Return enum values as choices for django form."""
        choices = []
        for option in cls:
            if exclude and option.value in exclude:
                continue
            key = option.value
            value = _('{}.{}'.format(trans_prefix, option.value)) if trans_prefix else option.value
            choices.append((key, value))
        return choices

    @classmethod
    def values_list(cls):
        """Return enum values as list."""
        return [option.value for option in cls]

    @classmethod
    def has_value(cls, value):
        """Check if there is any key defined with passed value."""
        return any(option.value == value for option in cls)

    @classmethod
    def has_key(cls, key):
        """Check if the key is defined in the enum."""
        return key in cls.__members__


class Genders(ChoiceEnum):
    """Enum defining genders."""

    female = 'female'
    male = 'male'
