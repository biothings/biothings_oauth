import functools
import urllib
from urllib.parse import urlencode

from tornado.web import HTTPError


def admin_required(handler_func):
    """
    Validates that the currently authenticated user is admin.

    :param handler_func: The handler function to be validated.
    :return: Original handler function return value in case of the user is
        admin.
    """
    @functools.wraps(handler_func)
    def wrapped_handler_func(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urllib.parse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        assert self.request.uri is not None
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return None
            raise HTTPError(403)

        if self.current_user.is_admin:
            return handler_func(self, *args, **kwargs)
        else:
            self.set_status(403)

    return wrapped_handler_func
