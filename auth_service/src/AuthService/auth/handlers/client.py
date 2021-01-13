import uuid
import secrets

from tornado.web import RequestHandler

from auth import APP_NAME
from auth.models import Client
from auth.forms import ClientForm
from helpers.handlers import HandlersHelper
from bases.handlers import BaseHandler


class ClientAddition(BaseHandler, RequestHandler):
    """
    Client addition handler for rendering Client addition form and saving new
    Client instance.
    """

    def get(self):
        """
        Handles rendering Client addition form.
        """
        self.render(
            f"{APP_NAME}/client/client_addition.html",
            result=None,
            form=ClientForm()
        )

    def post(self):
        """
        Handles saving a new instance to Client model.
        """

        form = HandlersHelper.build_request_form(self.request, ClientForm)

        if not form.validate():
            self.set_status(400)
            self.render(
                f"{APP_NAME}/client/client_addition.html",
                result="Could not add new Client instance! "
                       "Please fix the described errors first.",
                form=form
            )
            return

        client = Client(**form.data)
        client.client_id = uuid.uuid4()
        client.client_secret = secrets.token_urlsafe()[:25]

        self.db.add(client)
        self.db.commit()

        self.set_status(201)
        self.render(
            f"{APP_NAME}/client/client_addition.html",
            result="Client was saved successfully!",
            form=ClientForm()
        )


class ClientList(BaseHandler, RequestHandler):
    """
    Handles listing/deleting/and redirecting to editing Client instances.
    """

    def get(self):
        """
        Handles listing all existing Client instances ascending sorted by
        'created_at' field.
        """

        self.render(
            f"{APP_NAME}/client/client_list.html",
            clients=list(
                self.db
                    .query(Client)
                    .order_by(Client.created_at)
            ),
            result=None
        )


class ClientDeletion(BaseHandler, RequestHandler):
    """
    Handles deleting a Client instance.
    """

    def post(self, pk):
        """
        Delete a Client instance using its pk.

        Arguments:
            pk (int): Primary key (ID) of the Client instance to be deleted.
        """
        client = self.db\
            .query(Client)\
            .filter(Client.id == pk)\
            .first()

        if not client:
            self.set_status(404)
            return

        self.db.delete(client)
        self.db.commit()

        self.redirect(self.reverse_url("client_list"))


class ClientEdit(BaseHandler, RequestHandler):
    """
    Handles editing a Client instance.
    """

    def get(self, pk):
        """
        Handles rendering Client editing form.

        Arguments:
            pk (int): Primary key (ID) of the Client instance to be edited.
        """

        client = self.db\
            .query(Client)\
            .filter(Client.id == pk)\
            .first()

        if not client:
            self.set_status(404)
            return

        self.render(
            f"{APP_NAME}/client/client_edit.html",
            result=None,
            form=ClientForm(obj=client)
        )

    def post(self, pk):
        """
        Edits an existing Client instance.

        Arguments:
            pk (int): Primary key (ID) of the Client instance to be edited.
        """
        client = self.db.query(Client).filter(Client.id == pk).first()

        if not client:
            self.set_status(404)
            return

        form = HandlersHelper.build_request_form(self.request, ClientForm)

        if not form.validate():
            self.set_status(400)
            self.render(
                f"{APP_NAME}/client/client_edit.html",
                result="Could not save client instance! "
                       "Please fix the described errors first.",
                form=form
            )
            return

        form.populate_obj(client)
        self.db.commit()

        self.redirect(self.reverse_url("client_list"))
