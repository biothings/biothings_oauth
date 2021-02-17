import uuid
import secrets

from sqlalchemy.orm import subqueryload
import tornado
from tornado.web import RequestHandler

from auth import APP_NAME
from auth.models import Client, ClientApi, ClientApiScope, Api
from auth.forms import ClientForm
from helpers.handlers import HandlersHelper
from bases.handlers import BaseHandler


def user_controls_client(user, client):
    """
    Checks whether the given user can control the given client instance.

    @param user: The user to check against.
    @param client: The client to be checked.
    @return: True if the given user controls the given client, False otherwise.
    """

    return user.is_admin or user.id == client.user_id


class ClientAddition(BaseHandler, RequestHandler):
    """
    Client addition handler for rendering Client addition form and saving new
    Client instance.
    """

    @tornado.web.authenticated
    def get(self):
        """
        Handles rendering Client addition form.
        """
        self.render(
            f"{APP_NAME}/client/client_addition.html",
            result=None,
            form=ClientForm(db=self.db)
        )

    @tornado.web.authenticated
    def post(self):
        """
        Handles saving a new instance to Client model.
        """

        form = HandlersHelper.build_request_form(
            self.request, ClientForm, db=self.db
        )

        if not form.validate():
            self.set_status(400)
            self.render(
                f"{APP_NAME}/client/client_addition.html",
                result="Could not add new Client instance! "
                       "Please fix the described errors first.",
                form=form
            )
            return

        client = Client(user_id=self.current_user.id)
        form.populate_obj(client)
        client.client_id = uuid.uuid4()
        client.client_secret = secrets.token_urlsafe()[:25]

        self.db.add(client)
        self.db.commit()

        self.set_status(201)
        self.render(
            f"{APP_NAME}/client/client_addition.html",
            result="Client was saved successfully!",
            form=ClientForm(db=self.db)
        )


class ClientList(BaseHandler, RequestHandler):
    """
    Handles listing/deleting/and redirecting to editing Client instances.
    """

    @tornado.web.authenticated
    def get(self):
        """
        Handles listing all existing Client instances ascending sorted by
        'created_at' field.
        """

        # Return the appropriate clients based on user's role.
        clients = self.db.query(Client)

        if not self.current_user.is_admin:
            clients = clients.filter(Client.user_id == self.current_user.id)

        clients = list(clients.order_by(Client.created_at))

        self.render(
            f"{APP_NAME}/client/client_list.html",
            clients=clients,
            result=None
        )


class ClientDetail(BaseHandler, RequestHandler):
    """
    Handles displaying a Client instance's details.
    """

    @tornado.web.authenticated
    def get(self, pk):
        """
        Handles rendering a Client instance's details web page.

        Arguments:
            pk (int): Primary key (ID) of the Client instance.
        """

        client = self.db \
            .query(Client) \
            .options(
                subqueryload(Client.apis, ClientApi.api),
            ) \
            .filter(Client.id == pk) \
            .first()

        if not client:
            self.set_status(404)
            return
        if not user_controls_client(self.current_user, client):
            self.set_status(401)
            return

        self.render(
            f"{APP_NAME}/client/client_detail.html",
            client=client,
            result=None
        )


class ClientDeletion(BaseHandler, RequestHandler):
    """
    Handles deleting a Client instance.
    """

    @tornado.web.authenticated
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

        if not user_controls_client(self.current_user, client):
            self.set_status(401)
            return

        self.db.delete(client)
        self.db.commit()

        self.redirect(self.reverse_url("client_list"))


class ClientEdit(BaseHandler, RequestHandler):
    """
    Handles editing a Client instance.
    """

    @tornado.web.authenticated
    def get(self, pk):
        """
        Handles rendering Client editing form.

        Arguments:
            pk (int): Primary key (ID) of the Client instance to be edited.
        """

        client = self.db\
            .query(Client)\
            .options(subqueryload(Client.apis, ClientApi.api)) \
            .filter(Client.id == pk)\
            .first()

        if not client:
            self.set_status(404)
            return

        if not user_controls_client(self.current_user, client):
            self.set_status(401)
            return

        self.render(
            f"{APP_NAME}/client/client_edit.html",
            result=None,
            form=ClientForm(db=self.db, obj=client)
        )

    @tornado.web.authenticated
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

        if not user_controls_client(self.current_user, client):
            self.set_status(401)
            return

        form = HandlersHelper.build_request_form(
            self.request, ClientForm, db=self.db
        )

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

        self.redirect(self.reverse_url("client_detail", client.id))


class ClientApiScopesEdit(BaseHandler, RequestHandler):
    """
    Handles ClientApi scopes association.
    """

    @tornado.web.authenticated
    def get(self, pk, api_pk):
        client_api = self.db\
            .query(ClientApi)\
            .join(Client)\
            .filter(Client.id == pk)\
            .join(Api)\
            .filter(Api.id == api_pk)\
            .options(
                subqueryload(ClientApi.api, Api.scopes)
            )\
            .first()

        if not client_api:
            self.set_status(404)
            return

        if not user_controls_client(self.current_user, client_api.client):
            self.set_status(403)
            return

        api_scopes = client_api.api.scopes
        client_api_scopes = [
            client_api_scope.scope
            for client_api_scope in list(
                self.db
                    .query(ClientApiScope)
                    .filter(ClientApiScope.client_api_id == client_api.id)
                    .options(
                        subqueryload(ClientApiScope.scope)
                    )
            )
        ]

        for api_scope in api_scopes:
            api_scope.is_allowed = (api_scope in client_api_scopes)

        self.render(
            f"{APP_NAME}/client/clientapi_scopes_edit.html",
            api=client_api.api,
            api_scopes=api_scopes,
            result=None
        )

    @tornado.web.authenticated
    def post(self, pk, api_pk):
        client_api = self.db \
            .query(ClientApi)\
            .join(Client)\
            .filter(Client.id == pk)\
            .join(Api)\
            .filter(Api.id == api_pk)\
            .options(
                subqueryload(ClientApi.api, Api.scopes)
            )\
            .first()

        if not client_api:
            self.set_status(404)
            return

        if not user_controls_client(self.current_user, client_api.client):
            self.set_status(403)
            return

        client_api.scopes = []

        for api_scope in client_api.api.scopes:
            is_allowed = self.get_body_argument(
                f"api_scope_{api_scope.id}", None
            )
            if is_allowed and str(is_allowed) == "on":
                client_api.scopes.append(
                    ClientApiScope(
                        client_api_id=client_api.id,
                        scope_id=api_scope.id
                    )
                )

        self.db.commit()

        return self.redirect(self.reverse_url("client_detail", pk))
