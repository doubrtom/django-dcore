from django.shortcuts import reverse, redirect
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from re import compile


def force_default_language_middleware(get_response):
    """
    Ignore Accept-Language HTTP headers

    This will force the I18N machinery to always choose settings.LANGUAGE_CODE
    as the default initial language, unless another one is set via sessions or cookies

    Should be installed *before* any middleware that checks request.META['HTTP_ACCEPT_LANGUAGE'],
    namely django.middleware.locale.LocaleMiddleware

    Source: https://gist.github.com/vstoykov/1366794
    """

    def middleware(request):
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            del request.META['HTTP_ACCEPT_LANGUAGE']
        return get_response(request)

    return middleware


def force_login_middleware(get_response):
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.

    Source: http://onecreativeblog.com/post/59051248/django-login-required-middleware
    """

    exempt_urls = [compile(reverse(settings.LOGIN_URL))]
    if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
        exempt_urls += [compile(regex_url) for regex_url in settings.LOGIN_EXEMPT_URLS]

    def middleware(request: WSGIRequest):
        assert hasattr(request, 'user'), "The Login Required middleware\
                requires authentication middleware to be installed. Edit your\
                MIDDLEWARE_CLASSES setting to insert\
                'django.contrib.auth.middlware.AuthenticationMiddleware'. If that doesn't\
                work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
                'django.core.context_processors.auth'."

        if not request.user.is_authenticated:
            path = request.path_info
            if not any(m.match(path) for m in exempt_urls):
                return redirect(settings.LOGIN_URL)
        return get_response(request)

    return middleware
