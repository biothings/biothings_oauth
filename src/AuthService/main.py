import tornado.ioloop
from auth.handlers.auth import Login
from tornado.web import url, Application
from tornado.httpserver import HTTPServer

from AuthService import settings, database
from demo import views as demo_views
from core.handlers import Home
from auth.handlers import auth as auth_views
from auth.handlers.api import (
    ApiAddition, ApiList, ApiDeletion, ApiEdit, ApiDetail
)
from auth.handlers.client import (
    ClientAddition, ClientList, ClientDeletion, ClientEdit, ClientDetail
)
from auth.handlers.user import UserDetail


def make_app():
    db = database.Session()
    database.Base.metadata.create_all(bind=database.engine)

    urls = [
        # region core app
        url("/", Home, {"db": db}, name="home"),
        # endregion

        # region auth app

        # region API handlers
        url("/apis/", ApiList, {"db": db}, name="api_list"),
        url("/apis/add", ApiAddition, {"db": db}, name="api_addition"),
        url(
            r"/apis/(?P<pk>[0-9]+)/delete",
            ApiDeletion,
            {"db": db},
            name="api_deletion"
        ),
        url(
            r"/apis/(?P<pk>[0-9]+)",
            ApiDetail,
            {"db": db},
            name="api_detail"
        ),
        url(
            r"/apis/(?P<pk>[0-9]+)/edit",
            ApiEdit,
            {"db": db},
            name="api_edit"
        ),
        # endregion
        # region Client handlers
        url("/clients/", ClientList, {"db": db}, name="client_list"),
        url(
            "/clients/add",
            ClientAddition,
            {"db": db},
            name="client_addition"
        ),
        url(
            r"/clients/(?P<pk>[0-9]+)/delete",
            ClientDeletion,
            {"db": db},
            name="client_deletion"
        ),
        url(
            r"/clients/(?P<pk>[0-9]+)/edit",
            ClientEdit,
            {"db": db},
            name="client_edit"
        ),
        url(
            r"/clients/(?P<pk>[0-9]+)",
            ClientDetail,
            {"db": db},
            name="client_detail"
        ),
        # endregion
        # region Authentication handlers
        url(
            r"/oauth/github_auth",
            auth_views.GitHubAuth,
            {"db": db},
            name="github_auth"
        ),
        url(
            r"/oauth/token",
            auth_views.OAuthTokenIssuing,
            {"db": db},
            name="oauth_token_issuing"
        ),
        url(
            r"/.well-known/public-key",
            auth_views.PublicKeyHandler,
            name="public_key"
        ),
        url(
            r"/auth-demo",
            demo_views.ExampleAuthRequiredHandler,
            name="auth_demo"
        ),
        url(
            r"/scopes-demo",
            demo_views.ExampleScopeRequiredHandler,
            name="scopes_demo"
        ),
        # endregion
        # region Users
        url(settings.LOGIN_URL, Login, {"db": db}, name="login"),
        url(
            r"/user/(?P<pk>[0-9]+)",
            UserDetail,
            {"db": db},
            name="user_detail"
        ),
        # endregion

        # endregion
    ]

    return Application(
        template_path="templates",
        handlers=urls,
        debug=settings.DEBUG,
        xsrf_cookies=settings.XSRF_COOKIES,
        static_path=settings.STATIC_DIR,
        cookie_secret=settings.COOKIE_SECRET,
        login_url=settings.LOGIN_URL
    )


def main():
    app = make_app()
    server = HTTPServer(app)
    server.bind(8888)
    server.start(1 if settings.DEBUG else 0)  # forks one process per cpu
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
