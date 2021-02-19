from sqlalchemy import exists, and_
from sqlalchemy.orm import subqueryload
from tornado.web import RequestHandler
import tornado

from auth import APP_NAME
from auth.models import Api, ClientApi, Client
from auth.forms import ApiForm
from bases.handlers import BaseHandler
from helpers.decorators import admin_required
from helpers.handlers import HandlersHelper


class ApiAddition(BaseHandler, RequestHandler):
    """
    API addition handler for rendering API addition form and saving new API
    record.
    """

    @admin_required
    def get(self):
        """
        Handles rendering API addition form.
        """
        self.render(
            f"{APP_NAME}/api/api_addition.html",
            result=None,
            form=ApiForm()
        )

    @admin_required
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

    @tornado.web.authenticated
    def get(self):
        """
        Handles listing all existing API instances ascending sorted by
        'created_at' field.
        """
        apis = list(
            self.db
                .query(Api)
                .order_by(Api.created_at)
        )

        self.render(
            f"{APP_NAME}/api/api_list.html",
            apis=apis
        )


class ApiDetail(BaseHandler, RequestHandler):
    """
    Handles displaying an API instance's details.
    """

    @tornado.web.authenticated
    def get(self, pk):
        """
        Handles rendering an API instance's details web page.

        Arguments:
            pk (int): Primary key (ID) of the API instance.
        """

        if self.current_user.is_admin:
            api = self.db \
                .query(Api) \
                .options(
                    subqueryload(Api.clients, ClientApi.client),
                    subqueryload(Api.scopes)
                ) \
                .filter(Api.id == pk) \
                .first()
        else:
            api = self.db \
                .query(Api) \
                .options(
                    subqueryload(Api.scopes)
                ) \
                .filter(Api.id == pk) \
                .first()

        if not api:
            self.set_status(404)
            return

        # Return the appropriate clients based on user's role.
        if not self.current_user.is_admin:
            clients = list(
                self.db
                .query(Client)
                .filter(Client.user_id == self.current_user.id)
                .join(ClientApi)
                .filter(ClientApi.api_id == api.id)
            )
        else:
            clients = [client_api.client for client_api in api.clients]

        self.render(
            f"{APP_NAME}/api/api_detail.html",
            api=api,
            clients=clients,
            result=None
        )


class ApiDeletion(BaseHandler, RequestHandler):
    """
    Handles deleting an API instance.
    """

    @admin_required
    def post(self, pk):
        """
        Delete an API instance using its pk.

        Arguments:
            pk (int): Primary key (ID) of the API instance to be deleted.
        """
        api = self.db\
            .query(Api)\
            .filter(Api.id == pk)\
            .first()

        if not api:
            self.set_status(404)
            return

        self.db.delete(api)
        self.db.commit()

        self.redirect(self.reverse_url("api_list"))


class ApiEdit(BaseHandler, RequestHandler):
    """
    Handles editing an API instance.
    """

    @admin_required
    def get(self, pk):
        """
        Handles rendering API editing form.

        Arguments:
            pk (int): Primary key (ID) of the API instance to be edited.
        """

        api = self.db\
            .query(Api)\
            .filter(Api.id == pk)\
            .first()

        if not api:
            self.set_status(404)
            return

        self.render(
            f"{APP_NAME}/api/api_edit.html",
            result=None,
            form=ApiForm(obj=api)
        )

    @admin_required
    def post(self, pk):
        """
        Edits an existing API instance.

        Arguments:
            pk (int): Primary key (ID) of the API instance to be edited.
        """
        api = self.db \
            .query(Api) \
            .filter(Api.id == pk) \
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
