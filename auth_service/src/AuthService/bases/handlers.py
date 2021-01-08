class BaseHandler:
    """
    Base request handler.
    """
    def initialize(self, db):
        self.db = db
