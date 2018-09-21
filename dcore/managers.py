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
