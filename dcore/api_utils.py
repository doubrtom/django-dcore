from typing import Optional

from django import forms


def process_error_response_into_form_errors(
    form: forms.Form,
    error_data: dict,
    field_mapping: Optional[dict] = None
) -> bool:
    """It process error response from REST API.

    It tries to add errors from response into form as field errors
    or form errors.

    Args:
        form: Local form with invalid data.
        error_data: Error response from server in format of drf-friendly-errors.
        field_mapping: Mapping to allow display field error in another field.
            Mapping is in format error_data.field_name -> form.field_name.

    Returns:
        True if error data was processed else False.
    """
    code = error_data.get('code', None)
    if field_mapping is None:
        field_mapping = {}

    # 1000 = Validation Failed
    if code != '1000':
        return False

    for error in error_data.get('errors'):
        field = error.get('field')
        mapped_field = field_mapping.get(field, None)

        if mapped_field and mapped_field in form.fields.keys():
            form.add_error(mapped_field, error.get('message'))
            continue

        if field in form.fields.keys():
            form.add_error(field, error.get('message'))
            continue

        form.add_error(None, error.get('message'))
    return True
