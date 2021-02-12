from typing import Set
from collections import abc


# Define InheritanceModelSerializer only if there is rest_framework (djangorestframework) package:
try:
    from rest_framework import serializers
    from rest_framework.request import Request
    from rest_framework.settings import api_settings
except ImportError:
    pass  # Nothing to do, do not define InheritanceModelSerializer
else:
    class InheritanceModelSerializer(serializers.ModelSerializer):
        """Inheritance model serializer usable with django-rest-framework (djangorestframework)

        Examples:
            class CatSerializer(serializers.ModelSerializer):
                pass

            class DogSerializer(serializers.ModelSerializer):
                pass

            class AnimalSerializer(InheritanceModelSerializer):
                class Meta:
                    model = Animal
                    subtypes = {Dog: DogSerializer, Cat: CatSerializer}
                    subtypes_mapping = {'dog': DogSerializer, 'cat': CatSerializer}
                    subtype_keyword = 'animal_type'

            Incoming data: {"name": "kitty", "animal_type": "cat"}
        """

        def get_subclass(self, data=None):
            """Return instance of sub-serializer."""
            if data is None:
                data = self.initial_data

            if not isinstance(data, abc.Mapping):
                message = self.error_messages['invalid'].format(
                    datatype=type(data).__name__
                )
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: [message]
                }, code='invalid')

            sub_type = data.get(self.Meta.subtype_keyword, None)
            if sub_type is None or not isinstance(sub_type, str):
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: [
                        f'Missing inheritance type field: "{self.Meta.subtype_keyword}".'
                    ]
                }, code='invalid')

            serializer_class = self.Meta.subtypes_mapping.get(sub_type, None)
            if serializer_class is None:
                err_msg = f'Missing subtype class for keyword: "{self.Meta.subtype_keyword}".'
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: [err_msg]
                }, code='invalid')

            return serializer_class(data=data)

        def to_representation(self, instance):
            if not hasattr(self.Meta, 'subtypes'):
                raise ValueError('You have to define "subtypes" attribute in Meta class.')

            serializer = self.Meta.subtypes.get(type(instance))
            if serializer:
                return serializer(instance, context=self.context).data

            raise ValueError(
                'Unknown "{}" subclass of "{}" class, check your definition of Meta.subtypes '
                'in serializer for class "{}".'.format(
                    type(instance).__name__, self.Meta.model.__name__, self.Meta.model.__name__
                )
            )

        def to_internal_value(self, data):
            if not isinstance(data, abc.Mapping):
                message = self.error_messages['invalid'].format(
                    datatype=type(data).__name__
                )
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: [message]
                }, code='invalid')

            return self.get_subclass(data).to_internal_value(data)


    class DynamicFieldsSerializerMixin:
        """Mixin for django rest framework (djangorestframework) serializers to allow define fields in request URL.

        Define 'default_fields' in Meta class, it allows to send only some subset of all fields for
        default request without any special params.

        Define map 'field_groups' in format {'__group_name__': ('field1', 'field2'), ...} to allow use predefined field
        groups. Then in url use '.../endpoint/?fields=__group_name__' to get fields defined in the group.
        I suggest to use dunder names for groups to prevent any name collisions, i.e. __group_name__.
        There is automatically defined __all__ group, which returns all fields.
        (You can rename name of the group with attribute 'dynamic_fields_all_group_name')

        You can define exact fields with keyword: 'fields' (editable by 'dynamic_fields_include_key').
        Server then return ONLY these fields.

        You can add extra fields to default_fields with keyword: 'extra_fields' (editable by 'dynamic_fields_extra_key').
        Server then return all default_fields and these extra fields.

        You can exclude some fields from default_fields with keyword: 'exclude_fields'
        (editable by 'dynamic_fields_exclude_key').
        Server then return default_fields minus these excluded fields.

        All fields are separated by comma (e.g. fields=field1,field2,...).
        You can edit field separator by 'dynamic_fields_separator'.
        """

        dynamic_fields_extra_key = 'extra_fields'
        dynamic_fields_include_key = 'fields'
        dynamic_fields_exclude_key = 'exclude_fields'
        dynamic_fields_separator = ','
        dynamic_fields_all_group_name = '__all__'

        def get_dynamic_field_names(self, request) -> Set:
            """Return set of wanted fields defined by query param 'fields' or view field 'default_fields'."""
            includes_value = None
            if request:
                includes_value = request.query_params.get(self.dynamic_fields_include_key, None)

            field_groups = getattr(self.Meta, 'field_groups', {})
            field_groups[self.dynamic_fields_all_group_name] = self.Meta.fields

            if includes_value in field_groups:
                include_field_names = set(field_groups[includes_value])
            else:
                includes = []
                if request:
                    includes = request.query_params.getlist(self.dynamic_fields_include_key, [])
                include_field_names = {
                    name for names in includes for name in names.split(self.dynamic_fields_separator) if name
                }

            if not include_field_names and hasattr(self.Meta, 'default_fields'):
                include_field_names = set(self.Meta.default_fields)

            return include_field_names

        def get_exclude_field_names(self, request):
            """Return set of unwanted fields defined by query param 'exclude_fields'."""
            excludes = []
            if request:
                excludes = request.query_params.getlist(self.dynamic_fields_exclude_key, [])
            return {name for names in excludes for name in names.split(self.dynamic_fields_separator) if name}

        def get_extra_field_names(self, request):
            """Return set of extra wanted fields defined by query param 'extra_fields'.

            Extra fields are fields NOT returned by server for query without extra arguments (default set of fields).
            """
            extras = []
            if request:
                extras = request.query_params.getlist(self.dynamic_fields_extra_key, [])
            return {
                name for names in extras for name in names.split(self.dynamic_fields_separator) if name
            }

        @property
        def _readable_fields(self):
            if self.show_origin_fields:
                yield from super()._readable_fields
            else:
                for field in self.new_fields.values():
                    if not field.write_only:
                        yield field

        def to_representation(self, instance):
            self.show_origin_fields = False
            data = super().to_representation(instance)
            self.show_origin_fields = True
            return data

        def __init__(self, *args, **kwargs):
            extra_fields = kwargs.pop('extra_fields', None)
            super().__init__(*args, **kwargs)

            self.show_origin_fields = True
            self.new_fields = {**self.fields}

            request: Request = kwargs.get('context', {}).get('request', None)
            dynamic_field_names = self.get_dynamic_field_names(request)
            exclude_field_names = self.get_exclude_field_names(request)
            extra_field_names = self.get_extra_field_names(request)

            if extra_fields:
                extra_field_names = extra_field_names | set(extra_fields)

            if not dynamic_field_names and not exclude_field_names:
                return

            # If there is no dynamic_fields use defined fields in serializer.
            if not dynamic_field_names:
                dynamic_field_names = set(self.fields)

            field_names = (dynamic_field_names | extra_field_names) - exclude_field_names
            drop_field_names = set(self.fields) - field_names

            for field_name in drop_field_names:
                self.new_fields.pop(field_name)
