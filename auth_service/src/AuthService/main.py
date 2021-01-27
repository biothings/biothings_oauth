import tornado.ioloop
from tornado.web import url, Application
from tornado.httpserver import HTTPServer

from AuthService import settings, database
from demo import views as demo_views
from auth.handlers import auth as auth_views
from auth.handlers.api import ApiAddition, ApiList, ApiDeletion, ApiEdit
from auth.handlers.client import (
    ClientAddition, ClientList, ClientDeletion, ClientEdit
)


def make_app():
    db = database.Session()
    database.Base.metadata.create_all(bind=database.engine)

    urls = [
        # API handlers
        url("/apis/", ApiList, {"db": db}, name="api_list"),
        url("/apis/add", ApiAddition, {"db": db}, name="api_addition"),
        url(
            r"/apis/(?P<pk>[0-9]+)/delete",
            ApiDeletion,
            {"db": db},
            name="api_deletion"
        ),
        url(
            r"/apis/(?P<pk>[0-9]+)/edit",
            ApiEdit,
            {"db": db},
            name="api_edit"
        ),
        # Client handlers
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
        # Authentication handlers
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
    ]

    return Application(
        template_path="templates",
        handlers=urls,
        debug=settings.DEBUG,
        xsrf_cookies=settings.XSRF_COOKIES,
        static_path=settings.STATIC_DIR
    )


def main():
    app = make_app()
    server = HTTPServer(app)
    server.bind(8888)
    server.start(1 if settings.DEBUG else 0)  # forks one process per cpu
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
