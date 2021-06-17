import json
from urllib.parse import urlencode

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

register = template.Library()


@register.filter(name='divide')
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None


@register.filter(name='int_divide')
def int_divide(value, arg):
    try:
        return int(int(value) / int(arg))
    except (ValueError, ZeroDivisionError):
        return None


@register.filter(name='round_divide')
def round_divide(value, arg):
    try:
        return round(int(value) / int(arg))
    except (ValueError, ZeroDivisionError):
        return None


@register.filter(name='subtract')
def subtract(value, arg):
    try:
        return int(value) - int(arg)
    except (ValueError, ZeroDivisionError):
        return None


@register.filter(name='times')
def times(number):
    return range(number)


@register.filter(name='concatenate')
def concatenate(value, arg):
    return '{}{}'.format(value, arg)


@register.filter(name='getattr')
def getattr_filter(value, arg):
    return getattr(value, arg)


@register.filter(name='getitem')
def getitem(value, arg):
    try:
        return value[arg]
    except KeyError:
        return None


@register.filter(name='js', is_safe=True)
def js(value):
    return mark_safe(json.dumps(value))


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """Replace GET params by new value and return url encoded GET params."""
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)


@register.simple_tag(takes_context=False)
def trans_format(trans_key, **kwargs):
    """Trans text and call python str format on result."""
    translated: str = _(trans_key)
    return translated.format(**kwargs)


@register.simple_tag
def trans_concat(*args):
    """Concat all parts of tag and translate it."""
    return _(''.join(args))
