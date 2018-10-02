from django.db import models


class RemovedItemsManager(models.Manager):
    """Manager returning only removed items.

    Best use with django-model-utils.
    """

    def get_queryset(self):
        """
        Return queryset limited to removed entries.
        """
        kwargs = {'model': self.model, 'using': self._db}
        if hasattr(self, '_hints'):
            kwargs['hints'] = self._hints

        return self._queryset_class(**kwargs).filter(is_removed=True)


# Define InheritanceManager only if there is django_utils package:
try:
    from model_utils.managers import InheritanceManager as ModelUtilsInheritanceManager
except ImportError:
    pass  # Nothing to do, do not define InheritanceManager
else:
    class InheritanceManager(ModelUtilsInheritanceManager):
        """Inheritance manager usable with django-rest-framework (djangorestframework)

        This manager can be used to define inheritance serializers in django-rest-framework.
        See module serializers.
        """

        def all(self, *args, **kwargs):
            return super().all(*args, **kwargs).select_subclasses()
