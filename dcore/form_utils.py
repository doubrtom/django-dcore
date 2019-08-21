from django.forms import Form
from django.forms.utils import ErrorDict

from .exceptions import DependencyException


def form_errors_to_friendly_errors(
    form: Form,
    show_error_keyword: bool = False,
    show_field_class_name: bool = False
):
    """Take invalid form and return dict with errors in format of drf-friendly-errors package.

    To use this method you have to install drf-friendly-errors package!

    Args:
        show_error_keyword: If True each error contains also field 'keyword' with keyword representing error.
        show_field_class_name: If True each error contains also field 'field_class_name' with class name of the field.

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
            error_keyword = field_error.code

            if field_name == '__all__':
                # form error:
                field_class_name = None
                error_code = friendly_errors_settings.FRIENDLY_NON_FIELD_ERRORS.get(error_keyword, None)
            else:
                # field error:
                form_field = form.fields[field_name]
                field_class_name = form_field.__class__.__name__
                field_error_settings = friendly_errors_settings.FRIENDLY_FIELD_ERRORS.get(
                    field_class_name, {}
                )
                error_code = field_error_settings.get(error_keyword, None)

            friendly_error_dict = {
                'code': error_code,
                'field': field_name,
                'message': field_error.message,
            }
            if show_error_keyword:
                friendly_error_dict['keyword'] = error_keyword
            if show_field_class_name:
                friendly_error_dict['field_class_name'] = field_class_name
            errors.append(friendly_error_dict)

    return {
        'code': 1001,
        'message': 'Validation Failed',
        'errors': errors
    }
