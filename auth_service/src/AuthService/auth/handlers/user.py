import tornado
from tornado.web import RequestHandler

from bases.handlers import BaseHandler
from helpers.decorators import admin_required
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

        if user.id != self.current_user.id and not self.current_user.is_admin:
            self.set_status(403)
            return

        self.render(f"{APP_NAME}/user/user_detail.html", user=user)


class UserList(BaseHandler, RequestHandler):
    """
    Handles User list.
    """

    @admin_required
    def get(self):
        """
        Handles rendering User instance page.
        """

        users = list(
            self.db
            .query(User)
            .order_by(User.created_at)
        )

        self.render(f"{APP_NAME}/user/user_list.html", users=users)
