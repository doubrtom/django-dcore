# Define InheritanceModelSerializer only if there is rest_framework (djangorestframework) package:
try:
    from rest_framework import serializers
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
                return serializer(instance).data

            raise ValueError(
                'Unknown "{}" subclass of "{}" class, check your definition of Meta.subtypes '
                'in serializer for class "{}".'.format(
                    type(instance).__name__, self.Meta.model.__name__, self.Meta.model.__name__
                )
            )
