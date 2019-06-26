from django.forms import Field, TextInput
from django.utils.translation import gettext as _


class ListField(Field):
    widget = TextInput
    default_error_messages = {
        'invalid': _('Invalid list.'),
    }

    def __init__(self, *, child: Field, delimiter: str = ';', **kwargs):
        self.child = child
        self.delimiter = delimiter
        super().__init__(**kwargs)

        if not isinstance(child, Field):
            raise ValueError('Child field has to be instance of Field class/subclass.')

    def to_python(self, value):
        """
        Validate that each value separated by self.delimiter
        is valid according to self.child field.
        Return the result of int() or None for empty values.
        """
        value = super().to_python(value)
        if value in self.empty_values:
            return []

        items = []

        for item in str(value).split(self.delimiter):
            items.append(self.child.to_python(item))

        return items

    def prepare_value(self, value):
        return self.delimiter.join(value)
