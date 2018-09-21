class SessionStorage:
    """Class to save data into session section organized by section_id."""

    def __init__(self, session):
        self.session = session

    def set(self, section_id, key, value):
        """Set data to session section."""
        session_part = self.session.get(section_id, {})
        session_part[key] = value
        self.session[section_id] = session_part

    def get(self, section_id, key, default=None):
        """Get data from session section."""
        session_part = self.session.get(section_id, {})
        return session_part.get(key, default)

    def clear(self, section_id):
        """Clear session section."""
        try:
            del self.session[section_id]
            self.session.modified = True
        except KeyError:
            pass  # It is ok, value is already cleared.
