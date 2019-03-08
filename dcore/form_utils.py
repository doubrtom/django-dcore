from django.forms import Form
from django.forms.utils import ErrorDict

from .exceptions import DependencyException


def form_errors_to_friendly_errors(form: Form, show_error_keyword: bool = False):
    """Take invalid form and return dict with errors in format of drf-friendly-errors package.

    To use this method you have to install drf-friendly-errors package!

    Args:
        show_error_keyword: If True each error contains also field 'keyword' with keyword representing error.

    Returns:
        dict with errors
    """
    try:
        from rest_framework_friendly_errors.mixins import settings as friendly_errors_settings
    except ImportError:
        raise DependencyException(
            'To use form_utils.form_errors_to_friendly_errors you have to install drf-friendly-errors package.'
        )

    if form.is_valid():
        return {}

    errors = []
    errors_dict: ErrorDict = form._errors

    for field_name, error_list in errors_dict.items():
        for field_error in error_list.data:
            form_field = form.fields[field_name]
            field_error_settings = friendly_errors_settings.FRIENDLY_FIELD_ERRORS.get(
                form_field.__class__.__name__, {}
            )
            error_keyword = field_error.code
            error_code = field_error_settings.get(error_keyword)
            friendly_error_dict = {
                'code': error_code,
                'field': field_name,
                'message': field_error.message,
            }
            if show_error_keyword:
                friendly_error_dict['keyword'] = error_keyword
            errors.append(friendly_error_dict)

    return {
        'code': 1001,
        'message': 'Validation Failed',
        'errors': errors
    }
