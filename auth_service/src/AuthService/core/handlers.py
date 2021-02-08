import tornado
from bases.handlers import BaseHandler
from tornado.web import RequestHandler

from core import APP_NAME


class Home(BaseHandler, RequestHandler):
    """
    Handles home page.
    """

    @tornado.web.authenticated
    def get(self):
        """
        Handles rendering the home page.
        """

        self.render(f"{APP_NAME}/home.html", auth_error=None)
