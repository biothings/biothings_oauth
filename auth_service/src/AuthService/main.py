import tornado.ioloop
from tornado.web import url, RequestHandler, Application
from tornado.httpserver import HTTPServer

from AuthService import settings, database
from demo import models


class MainHandler(RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        user = models.User(
                name="Test", fullname="Test User", nickname="test"
            )
        self.db.add(user)
        self.db.commit()

        self.write(
            {"result": f"Created a new user {user}"}
        )


def make_app():
    db = database.Session()
    database.Base.metadata.create_all(bind=database.engine)

    urls = [
        url(r"/", MainHandler, {"db": db}, name="main_handler"),
    ]

    return Application(handlers=urls, debug=settings.DEBUG)


def main():
    app = make_app()
    server = HTTPServer(app)
    server.bind(8888)
    server.start(1 if settings.DEBUG else 0)  # forks one process per cpu
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
