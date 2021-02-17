import hashlib
import json
import datetime
import os
import requests

from requests_oauthlib import OAuth2Session
from sqlalchemy.orm import subqueryload
from sqlalchemy.sql.expression import true
from tornado.web import RequestHandler
from authlib.jose import jwt, JsonWebKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend

from helpers.memcached import get_memcached_client
from AuthService import settings
from bases.handlers import BaseHandler, XsrfExemptedHandler
from auth.models import (
    Client, ClientApi, Scope, User, UserIdentityProvider, ClientApiScope
)
from core import APP_NAME as CORE_APP_NAME
from auth import APP_NAME


class PublicKeyHandler(RequestHandler):
    def get(self):
        key_data = JsonWebKey.import_key(
            settings.PUBLIC_KEY.encode("UTF-8"), {'kty': 'RSA'}
        )
        self.write(key_data.as_json())


class OAuthTokenIssuing(XsrfExemptedHandler, BaseHandler, RequestHandler):

    @staticmethod
    def _get_exp_timestamp():
        """
        Returns the exp claim value in UTC timestamp.

        Returns:
             (int): Timestamp in UTC.
        """

        return int(
            (
                    datetime.datetime.utcnow() +
                    datetime.timedelta(minutes=settings.JWT_EXP_IN_MINUTES)
            )
            .replace(tzinfo=datetime.timezone.utc)
            .timestamp()
        )

    def _get_valid_client_secret(self, client_id):
        client = self.db\
            .query(Client)\
            .filter(Client.client_id == client_id)\
            .first()

        return None if not client else client.client_secret

    def _get_client_authorized_scopes(self, client_id):
        authorized_client_api_ids = self.db\
            .query(ClientApi.api_id)\
            .join(Client)\
            .filter(
                Client.client_id == client_id,
                Client.authorized == true()
            )\
            .subquery()

        authorized_scopes = list(
            self.db
                .query(ClientApiScope)
                .join(Scope)
                .filter(Scope.api_id.in_(authorized_client_api_ids))
                .options(subqueryload(ClientApiScope.scope))
        )
        # Maybe serialize the data that needs to be included in the JWT.
        # Currently, we return only Scope.name.
        authorized_scopes_names = [
            client_api_scope.scope.name
            for client_api_scope in authorized_scopes
        ]
        return ' '.join(authorized_scopes_names)

    def _return_jwt(self, client_id):
        header = {'alg': 'RS256', 'typ': 'JWT'}
        payload = {
            'iss': f"https://{settings.AUTH_SERVICE_DOMAIN}/",
            'sub': client_id,
            'exp': self._get_exp_timestamp(),
            'scope': self._get_client_authorized_scopes(client_id)
        }
        key = load_pem_private_key(
            settings.PRIVATE_KEY.encode("UTF-8"),
            password=None,
            backend=default_backend()
        )
        access_token = jwt.encode(header, payload, key)
        self.set_status(200)
        self.write({
            'access_token': access_token.decode('ascii'),
            'token_type': 'Bearer',
        })

    def post(self):
        try:
            request_body = json.loads(self.request.body or "{}")
            audience = request_body['audience']
            grant_type = request_body['grant_type']
            client_id = request_body['client_id']
            client_secret = request_body['client_secret']
        except KeyError:
            # TODO: Refine the error message to be more informative.
            self.set_status(
                400, 'Bad request body (missing required field/s).'
            )
            return

        valid_client_secret = self._get_valid_client_secret(client_id)
        if valid_client_secret and client_secret == valid_client_secret:
            self._return_jwt(client_id)
        else:
            self.set_status(401)


class GitHubAuth(BaseHandler, RequestHandler):
    """
    Handles the user authentication process using Github.
    """
    __client_id = os.environ.get("GITHUB_CLIENT_ID")
    __client_secret = os.environ.get("GITHUB_CLIENT_SECRET")

    def post(self):
        """
        Handles initializing the OAuth2 flow and redirecting to GitHub access
        consent confirmation.
        """

        auth_base_url = os.environ.get("AUTH_BASE_URL")
        github = OAuth2Session(self.__client_id)

        auth_url, state = github.authorization_url(auth_base_url)
        state_md5_hash = hashlib.md5(state.encode('UTF-8')).hexdigest()

        memcached_client = get_memcached_client()
        memcached_client.set(
            key=state_md5_hash, value=state_md5_hash, time=10 * 60
        )

        self.redirect(auth_url)

    def _set_new_user_cookie(self, user):
        """
        Sets a new secret cookie for the successfully authenticated user.

        Arguments:
            user (auth.models.User): Successfully authenticated user.
        """
        cookie_expires_after = \
            int(os.environ.get("COOKIE_EXPIRES_AFTER"))
        self.set_secure_cookie(
            "_pk", str(user.id), expires_days=cookie_expires_after
        )

    def _update_or_create_user(self, github_user):
        """
        Creates/Updates a new/existing user after authentication.

        Arguments:
            github_user(dict): Json response of API call to Github user's data.
        Returns:
            user(auth.models.User): User instance.
        """

        user = self.db \
            .query(User) \
            .filter(
                User.identity_provider_user_id == github_user["id"]
            ) \
            .filter(
                User.identity_provider == UserIdentityProvider.GITHUB
            ) \
            .first()

        if not user:
            user = User()

        user.identity_provider = UserIdentityProvider.GITHUB
        user.username = github_user["login"]
        user.identity_provider_user_id = github_user["id"]
        user.last_identity_provider_authentication = \
            datetime.datetime.utcnow()

        self.db.add(user)
        self.db.commit()

        return user

    def get(self):
        token_url = os.environ.get("TOKEN_URL")
        state = self.get_query_argument("state")
        state_md5_hash = hashlib.md5(state.encode('UTF-8')).hexdigest()

        memcached_client = get_memcached_client()

        if memcached_client.get(state_md5_hash):
            github = OAuth2Session(self.__client_id)
            try:
                github.fetch_token(
                    token_url,
                    client_secret=self.__client_secret,
                    authorization_response=self.request.full_url()
                )
            except Exception:
                self.render(
                    f"{CORE_APP_NAME}/home.html",
                    auth_error="Failed to sign in. Please try again!"
                )
                return

            github_user_response = github.get('https://api.github.com/user')

            if github_user_response.status_code != requests.codes.OK:
                self.render(
                    f"{CORE_APP_NAME}/home.html",
                    auth_error="Failed to sign in. Please try again!"
                )
                return
            else:
                github_user = github_user_response.json()
                user = self._update_or_create_user(github_user)

                self._set_new_user_cookie(user)

                self.redirect(self.reverse_url("user_detail", user.id))
        else:
            self.render(
                f"{CORE_APP_NAME}/home.html",
                auth_error="Bad/Not Allowed sign in attempt. Please try again!"
            )


class Login(BaseHandler, RequestHandler):
    """
    Handles user's login.
    """

    def get(self):
        """
        Handles rendering user login options.
        """
        self.render(f"{APP_NAME}/login.html")
