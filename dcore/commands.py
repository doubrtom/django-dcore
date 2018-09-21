import uuid

from .service import SessionStorage


class SaveDataToSessionCommand:
    """Command to save data into session section organized by token.

    If there is no token passed, commands generate one as UUID version 4.
    """

    def __init__(self, session):
        self.storage = SessionStorage(session)

    def execute(self, key, value, token=None):
        """Save data to session section identified by token."""
        if token is None:
            token = self._generate_token()
        self.storage.set(token, key, value)
        return token

    def _generate_token(self):
        """Generate token to organize data into section."""
        return str(uuid.uuid4())


class LoadDataFromSessionCommand:
    """Command to load data from session section organized by token."""

    def __init__(self, session):
        self.storage = SessionStorage(session)

    def execute(self, key, token, default=None):
        """Return data from session section identified by token."""
        return self.storage.get(token, key, default)
