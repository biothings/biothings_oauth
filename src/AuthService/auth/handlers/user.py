import tornado
from tornado.web import RequestHandler

from bases.handlers import BaseHandler
from auth import APP_NAME
from auth.models import User


class UserDetail(BaseHandler, RequestHandler):
    """
    Handles user detail.
    """

    @tornado.web.authenticated
    def get(self, pk):
        """
        Handles rendering the user detail page.

        Arguments:
            pk(int): User's ID.
        """

        user = self.db \
            .query(User) \
            .filter(User.id == pk) \
            .first()

        if not user:
            self.set_status(404)
            return

        self.render(f"{APP_NAME}/user/user_detail.html", user=user)
