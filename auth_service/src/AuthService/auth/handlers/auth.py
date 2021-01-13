import json

from sqlalchemy.sql.expression import true
from tornado.web import RequestHandler
from authlib.jose import jwt, JsonWebKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend

from AuthService import settings
from bases.handlers import BaseHandler, XsrfExemptedHandler
from auth.models import Client, ClientApi, Scope


class PublicKeyHandler(RequestHandler):
    def get(self):
        key_data = JsonWebKey.import_key(
            settings.PUBLIC_KEY.encode("UTF-8"), {'kty': 'RSA'}
        )
        self.write(key_data.as_json())


class OAuthTokenIssuing(XsrfExemptedHandler, BaseHandler, RequestHandler):

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
                .query(Scope)
                .filter(Scope.api_id.in_(authorized_client_api_ids))
        )
        # Maybe serialize the data that needs to be included in the JWT.
        # Currently, we return only Scope.name.
        authorized_scopes_names = [scope.name for scope in authorized_scopes]
        return ' '.join(authorized_scopes_names)

    def _return_jwt(self, client_id):
        scopes = self._get_client_authorized_scopes(client_id)
        header = {'alg': 'RS256', 'typ': 'JWT'}
        payload = {
            'iss': f"https://{settings.AUTH_SERVICE_DOMAIN}/",
            'sub': '123',
            'scope': scopes
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
            'expires_in': 'TODO'
        })

    def post(self):
        try:
            request_body = json.loads(self.request.body or "{}")
            audience = request_body['audience']
            grant_type = request_body['grant_type']
            client_id = request_body['client_id']
            client_secret = request_body['client_secret']
        except KeyError:
            self.set_status(
                400, 'Bad request body (missing required field/s).'
            )
            return

        valid_client_secret = self._get_valid_client_secret(client_id)
        if valid_client_secret and client_secret == valid_client_secret:
            self._return_jwt(client_id)
        else:
            self.set_status(401)
