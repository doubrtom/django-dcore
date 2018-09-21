import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


def hex_color_validator(value):
    """Validate HEX color format."""

    regex = r'^#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$'  # For example blue color: #0000FF or #00F
    match = re.search(regex, value)
    if not match:
        raise ValidationError(_('dcore.validators.invalid_hex_color'))
