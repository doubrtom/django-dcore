from django.urls import resolve


def common(request):
    """Set common context to template.

    Context variables:
    - app_name = Name of active django app.
    - path_name = Name of active django URL path.
    """
    return {
        'app_name': resolve(request.path).app_name,
        'path_name': resolve(request.path).url_name
    }
