from django.db import models
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor


# source: https://github.com/jazzband/django-model-utils/issues/11
class InheritanceForwardManyToOneDescriptor(ForwardManyToOneDescriptor):
    def get_queryset(self, **hints):
        return self.field.remote_field.model.objects.db_manager(hints=hints).select_subclasses()


# source: https://github.com/jazzband/django-model-utils/issues/11
class InheritanceForeignKey(models.ForeignKey):
    """Foreign key, that return concrete subclass.

    Usable only with django-model-utils package !!
    """
    forward_related_accessor_class = InheritanceForwardManyToOneDescriptor
