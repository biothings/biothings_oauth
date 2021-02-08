import os

from auth.models import User


class BaseHandler:
    """
    Base request handler.
    """
    def initialize(self, db):
        self.db = db

    def get_current_user(self):
        """
        Handles getting the authenticated user making a request.

        Returns:
            user (auth.models.User): The currently authenticated user.
        """

        cookie_expires_after = int(os.environ.get("COOKIE_EXPIRES_AFTER"))
        pk = self.get_secure_cookie("_pk", max_age_days=cookie_expires_after)

        if not pk:
            return

        return self.db.query(User).filter(User.id == int(pk)).first()


class XsrfExemptedHandler:
    """
    A handler with XSRF checking disabled.
    """

    def check_xsrf_cookie(self) -> None:
        pass
