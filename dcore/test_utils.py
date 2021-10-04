import json
from typing import Collection, Iterable, Union


class DoNotAssert:
    """Class to mark function argument not intended for assert."""
    pass


# Singleton of DoNotAssert class.
# Use it to mark assert function argument as not intended for assert.
do_not_assert = DoNotAssert()


def __assert_one_sub_error_in_drf_friendly_error_response(
    error_dict: dict,
    response_json: dict,
    error_code: Union[int, DoNotAssert] = do_not_assert,
    field: Union[str, DoNotAssert] = do_not_assert,
    message: Union[str, DoNotAssert] = do_not_assert
):
    """Take dict with one DRF sub-error in drf-friendly-errors format and assert values in it.

    Taking one value from response_json['errors'] array.

    Args:
        error_dict: Dict with error values.
        response_json: Decoded DRF response.
        error_code: Error code of one expected error.
        field: Field of one expected error.
        message: Message of one expected error.
    """
    if not isinstance(error_code, DoNotAssert):
        assert int(error_dict['code']) == error_code, response_json
    if not isinstance(field, DoNotAssert):
        assert error_dict['field'] == field, response_json
    if not isinstance(message, DoNotAssert):
        assert error_dict['message'] == message, response_json


def assert_drf_friendly_error(
    response,
    response_status_code: int = 400,
    main_error_code: int = 1001,
    main_error_message: str = 'Validation Failed',
    error_code: Union[int, DoNotAssert] = do_not_assert,
    field: Union[str, DoNotAssert] = do_not_assert,
    message: Union[str, DoNotAssert] = do_not_assert
):
    """Take DRF response and assert one error in drf-friendly-errors format.

    Args:
        response: DRF response.
        response_status_code: Expected HTTP status code in response.
        main_error_code: Main code in response.
        main_error_message: Main message in response.
        error_code: Error code of one expected error.
        field: Field of one expected error.
        message: Message of one expected error.
    """
    assert response.status_code == response_status_code

    response_json = json.loads(response.content.decode(encoding='utf-8'))

    assert int(response_json['code']) == main_error_code, response_json
    assert response_json['message'] == main_error_message, response_json
    assert len(response_json['errors']) == 1, response_json
    err = response_json['errors'][0]
    __assert_one_sub_error_in_drf_friendly_error_response(err, response_json, error_code, field, message)


def assert_drf_friendly_errors(
    response,
    expected_errors: Collection[dict],
    response_status_code: int = 400,
    main_error_code: int = 1001,
    main_error_message: str = 'Validation Failed'
):
    """Take DRF response and assert multiple errors in drf-friendly-errors format.

    Args:
        response: DRF response.
        expected_errors: List of expected errors in dict format: {'error_code': x, 'field': y, 'message': message}.
            You can use "do_not_assert" value to skip assertion of one key, or just don't insert that key in dict.
        response_status_code: Expected HTTP status code in response.
        main_error_code: Main code in response.
        main_error_message: Main message in response.
    """
    assert response.status_code == response_status_code

    response_json = json.loads(response.content.decode(encoding='utf-8'))

    assert int(response_json['code']) == main_error_code, response_json
    assert response_json['message'] == main_error_message, response_json
    assert len(response_json['errors']) == len(expected_errors), response_json
    for index, expected_error in enumerate(expected_errors):
        __assert_one_sub_error_in_drf_friendly_error_response(
            response_json['errors'][index],
            response_json,
            expected_error.get('error_code', do_not_assert),
            expected_error.get('field', do_not_assert),
            expected_error.get('message', do_not_assert)
        )


# Define pytest-factoryboy utils only if there is pytest-factoryboy (pytest-factoryboy) package:
try:
    from factory import Factory
    from factory.base import StubObject
except ImportError:
    pass  # Nothing to do, do not define InheritanceModelSerializer
else:

    class DictFactory:
        """Convert other factory output into dict."""

        def __init__(self, factory: Factory):
            self.factory = factory

        def create(self, **kwargs):
            stub = self.factory.stub(**kwargs)
            stub_dict = self.__convert_dict_from_stub(stub)
            return stub_dict

        def create_batch(self, size: int, **kwargs):
            stubs = self.factory.stub_batch(size, **kwargs)
            stub_dict = [self.__convert_dict_from_stub(stub) for stub in stubs]
            return stub_dict

        def __is_stub_of_list(self, stub: StubObject) -> bool:
            try:
                return all(k.isdigit() for k in stub.__dict__.keys())
            except AttributeError:
                return False

        def __convert_dict_from_stub(self, field):
            if isinstance(field, StubObject):
                if self.__is_stub_of_list(field):
                    return [self.__convert_dict_from_stub(v) for v in field.__dict__.values()]
                return {k: self.__convert_dict_from_stub(v) for k, v in field.__dict__.items()}
            if isinstance(field, Iterable) and all(isinstance(x, StubObject) for x in field):
                return [self.__convert_dict_from_stub(v) for v in field]
            else:
                return field


    def create_post_generation_list(factory, size: int, field_name, created_object, create, extracted, **kwargs):
        """Universal function to add items from factory into created_object. Use this in post_generation hook.

        This method support post_generation adding for object, stub or dict factory output format.
        For generating dict from Factory see DictFactory in this module.
        """
        if create:
            if extracted is None:
                items = factory.create_batch(size, **kwargs)
            else:
                items = extracted
            for item in items:
                getattr(created_object, field_name).add(item)
        else:
            if extracted is None:
                items = factory.stub_batch(size, **kwargs)
            else:
                items = extracted
            setattr(created_object, field_name, items)
