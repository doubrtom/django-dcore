class ImproperlyConfigured(Exception):
    """Throw it, when there is invalid configuration in settings."""
    pass


class InvalidData(Exception):
    """Throw it, when processed data are invalid."""
    pass


class MissingArgumentException(Exception):
    """Throw it, when there is missing argument(s)."""
    pass


class LogicException(Exception):
    """Throw it, when program should never reach throwing statement, i.e. logic error in program."""
    pass


class DependencyException(Exception):
    """Throw it, when missing optional dependency."""
    pass
