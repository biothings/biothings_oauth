import datetime
import uuid
import secrets

from sqlalchemy import exists, and_
from tornado.web import RequestHandler

from bases.handlers import BaseHandler
from auth.models import Api, Client
from auth.forms import ApiForm, ClientForm
from helpers.handlers import HandlersHelper

APP_NAME = "auth"


class ApiAddition(BaseHandler, RequestHandler):
    """
    API addition handler for rendering API addition form and saving new API
    record.
    """

    def get(self):
        """
        Handles rendering API addition form.
        """
        self.render(
            f"{APP_NAME}/api/api_addition.html",
            result=None,
            form=ApiForm()
        )

    def post(self):
        """
        Handles saving a new instance to Api model.
        """

        form = HandlersHelper.build_request_form(self.request, ApiForm)

        if not form.validate():
            self.set_status(400)
            self.render(
                f"{APP_NAME}/api/api_addition.html",
                result="Could not save new API instance! "
                       "Please fix the described errors first.",
                form=form
            )
            return

        if self.db.query(
                exists().where(Api.identifier == form.identifier.data)
        ).scalar():
            self.set_status(409)
            self.render(
                f"{APP_NAME}/api/api_addition.html",
                result=f"An instance with "
                       f"identifier='{form.identifier.data}' "
                       f"already exists!",
                form=form
            )
            return

        self.db.add(Api(**form.data))
        self.db.commit()

        self.set_status(201)
        self.render(
            f"{APP_NAME}/api/api_addition.html",
            result="API was saved successfully!",
            form=ApiForm()
        )


class ApiList(BaseHandler, RequestHandler):
    """
    Handles listing/deleting/and redirecting to editing API instances.
    """

    def get(self):
        """
        Handles listing all existing API instances ascending sorted by
        'created_at' field.
        """

        self.render(
            f"{APP_NAME}/api/api_list.html",
            apis=list(
                self.db
                    .query(Api)
                    .filter(Api.deleted_at.is_(None))
                    .order_by(Api.created_at)
            )
        )


class ApiDeletion(BaseHandler, RequestHandler):
    """
    Handles deleting an API instance.
    """

    def post(self, pk):
        """
        Delete an API instance using its pk.

        Arguments:
            pk (int): Primary key (ID) of the API instance to be deleted.
        """
        api = self.db\
            .query(Api)\
            .filter(Api.id == pk, Api.deleted_at.is_(None))\
            .first()

        if not api:
            self.set_status(404)
            return

        api.deleted_at = datetime.datetime.utcnow()
        self.db.commit()

        self.redirect(self.reverse_url("api_list"))


class ApiEdit(BaseHandler, RequestHandler):
    """
    Handles editing an API instance.
    """

    def get(self, pk):
        """
        Handles rendering API editing form.

        Arguments:
            pk (int): Primary key (ID) of the API instance to be edited.
        """

        api = self.db\
            .query(Api)\
            .filter(Api.id == pk, Api.deleted_at.is_(None))\
            .first()

        if not api:
            self.set_status(404)
            return

        self.render(
            f"{APP_NAME}/api/api_edit.html",
            result=None,
            form=ApiForm(obj=api)
        )

    def post(self, pk):
        """
        Edits an existing API instance.

        Arguments:
            pk (int): Primary key (ID) of the API instance to be edited.
        """
        api = self.db \
            .query(Api) \
            .filter(Api.id == pk, Api.deleted_at.is_(None)) \
            .first()

        if not api:
            self.set_status(404)
            return

        form = HandlersHelper.build_request_form(self.request, ApiForm)

        if not form.validate():
            self.set_status(400)
            self.render(
                f"{APP_NAME}/api/api_edit.html",
                result="Could not save API instance! "
                       "Please fix the described errors first.",
                form=form
            )
            return

        if self.db.query(
                exists().where(
                    and_(
                        Api.identifier == form.identifier.data,
                        Api.id != api.id
                    )
                )
        ).scalar():
            self.set_status(409)
            self.render(
                f"{APP_NAME}/api/api_edit.html",
                result=f"An instance with "
                       f"identifier='{form.identifier.data}' "
                       f"already exists!",
                form=form
            )
            return

        form.populate_obj(api)
        self.db.commit()

        self.redirect(self.reverse_url("api_list"))


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
                    .filter(Client.deleted_at.is_(None))
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
            .filter(Client.id == pk, Client.deleted_at.is_(None))\
            .first()

        if not client:
            self.set_status(404)
            return

        client.deleted_at = datetime.datetime.utcnow()
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
            .filter(Client.id == pk, Client.deleted_at.is_(None))\
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
