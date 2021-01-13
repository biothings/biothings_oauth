class BaseHandler:
    """
    Base request handler.
    """
    def initialize(self, db):
        self.db = db


class XsrfExemptedHandler:
    """
    A handler with XSRF checking disabled.
    """

    def check_xsrf_cookie(self) -> None:
        pass
