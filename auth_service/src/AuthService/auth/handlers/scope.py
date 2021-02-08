from sqlalchemy import exists
import tornado
from tornado.web import RequestHandler

from helpers.handlers import HandlersHelper
from bases.handlers import BaseHandler
from auth import APP_NAME
from auth.models import Scope, Api
from auth.forms import ScopeForm


class ScopeAddition(BaseHandler, RequestHandler):
    """
    Scope addition handler for rendering Scope addition form and saving new
    Scope record.
    """

    @tornado.web.authenticated
    def get(self, api_pk):
        """
        Handles rendering Scope addition form.
        """
        self.render(
            f"{APP_NAME}/scope/scope_addition.html",
            result=None,
            form=ScopeForm()
        )

    @tornado.web.authenticated
    def post(self, api_pk):
        """
        Handles saving a new instance to Scope model.

        Arguments:
            api_pk (int): The API ID to add the Scope to.
        """

        form = HandlersHelper.build_request_form(self.request, ScopeForm)

        if not form.validate():
            self.set_status(400)
            self.render(
                f"{APP_NAME}/scope/scope_addition.html",
                result="Could not save new Scope instance! "
                       "Please fix the described errors first.",
                form=form
            )
            return

        if self.db.query(
                exists().
                where(Scope.api_id == api_pk).
                where(Scope.name == form.name.data)
        ).scalar():
            self.set_status(409)
            self.render(
                f"{APP_NAME}/scope/scope_addition.html",
                result=f"This API already has a scope with name='"
                       f"{form.name.data}' !",
                form=form
            )
            return

        self.db.add(Scope(api_id=api_pk, **form.data))
        self.db.commit()

        self.set_status(201)
        self.render(
            f"{APP_NAME}/scope/scope_addition.html",
            result="Scope was added successfully!",
            form=ScopeForm()
        )


class ScopeDeletion(BaseHandler, RequestHandler):
    """
    Handles deleting a Scope instance.
    """

    @tornado.web.authenticated
    def post(self, api_pk, pk):
        """
        Delete a Scope instance using its pk.

        Arguments:
            api_pk (int): The ID of the API that has this Scope.
            pk (int): Primary key (ID) of the Scope instance to be deleted.
        """
        scope = self.db\
            .query(Scope)\
            .filter(Scope.api_id == api_pk)\
            .filter(Scope.id == pk)\
            .first()

        if not scope:
            self.set_status(404)
            return

        self.db.delete(scope)
        self.db.commit()

        self.redirect(self.reverse_url("api_detail", api_pk))


class ScopeEdit(BaseHandler, RequestHandler):
    """
    Handles editing a Scope instance.
    """

    @tornado.web.authenticated
    def get(self, api_pk, pk):
        """
        Handles rendering Scope editing form.

        Arguments:
            api_pk (int): The ID of the API that has this Scope.
            pk (int): Primary key (ID) of the Scope instance to be edited.
        """

        scope = self.db\
            .query(Scope)\
            .filter(Scope.api_id == api_pk)\
            .filter(Scope.id == pk)\
            .first()

        if not scope:
            self.set_status(404)
            return

        self.render(
            f"{APP_NAME}/scope/scope_edit.html",
            result=None,
            form=ScopeForm(obj=scope)
        )

    @tornado.web.authenticated
    def post(self, api_pk, pk):
        """
        Edits an existing Scope instance.

        Arguments:
            api_pk (int): The ID of the API that has this Scope.
            pk (int): Primary key (ID) of the Scope instance to be edited.
        """
        scope = self.db \
            .query(Scope) \
            .filter(Scope.api_id == api_pk) \
            .filter(Scope.id == pk) \
            .first()

        if not scope:
            self.set_status(404)
            return

        form = HandlersHelper.build_request_form(self.request, ScopeForm)

        if not form.validate():
            self.set_status(400)
            self.render(
                f"{APP_NAME}/scope/scope_edit.html",
                result="Could not save Scope instance! "
                       "Please fix the described errors first.",
                form=form
            )
            return

        if self.db.query(
                exists()
                .where(Scope.api_id != api_pk)
                .where(Scope.name == form.name.data)
        ).scalar():
            self.set_status(409)
            self.render(
                f"{APP_NAME}/scope/scope_edit.html",
                result=f"This API already has a scope with name='"
                       f"{form.name.data}' !",
                form=form
            )
            return

        form.populate_obj(scope)
        self.db.commit()

        self.redirect(self.reverse_url("api_detail", api_pk))
