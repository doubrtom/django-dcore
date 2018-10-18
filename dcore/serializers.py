from typing import Set


# Define InheritanceModelSerializer only if there is rest_framework (djangorestframework) package:
try:
    from rest_framework import serializers
    from rest_framework.request import Request
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
        """

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
            includes_value = request.query_params.get(self.dynamic_fields_include_key)

            field_groups = getattr(self.Meta, 'field_groups', {})
            field_groups[self.dynamic_fields_all_group_name] = self.Meta.fields

            if includes_value in field_groups:
                include_field_names = set(field_groups[includes_value])
            else:
                includes = request.query_params.getlist(self.dynamic_fields_include_key)
                include_field_names = {
                    name for names in includes for name in names.split(self.dynamic_fields_separator) if name
                }

            if not include_field_names and hasattr(self.Meta, 'default_fields'):
                include_field_names = set(self.Meta.default_fields)

            return include_field_names

        def get_exclude_field_names(self, request):
            """Return set of unwanted fields defined by query param 'exclude_fields'."""
            excludes = request.query_params.getlist(self.dynamic_fields_exclude_key)
            return {name for names in excludes for name in names.split(self.dynamic_fields_separator) if name}

        def get_extra_field_names(self, request):
            """Return set of extra wanted fields defined by query param 'extra_fields'.

            Extra fields are fields NOT returned by server for query without extra arguments (default set of fields).
            """
            extras = request.query_params.getlist(self.dynamic_fields_extra_key)
            return {
                name for names in extras for name in names.split(self.dynamic_fields_separator) if name
            }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            request: Request = kwargs.get('context', {}).get('request')

            if not request or request.method != 'GET':
                return

            dynamic_field_names = self.get_dynamic_field_names(request)
            exclude_field_names = self.get_exclude_field_names(request)
            extra_field_names = self.get_extra_field_names(request)

            if not dynamic_field_names and not exclude_field_names:
                return

            # If there is no dynamic_fields use defined fields in serializer.
            if not dynamic_field_names:
                dynamic_field_names = set(self.fields)

            field_names = (dynamic_field_names | extra_field_names) - exclude_field_names
            drop_field_names = set(self.fields) - field_names

            for field_name in drop_field_names:
                self.fields.pop(field_name)
