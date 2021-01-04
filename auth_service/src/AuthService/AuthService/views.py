import json

from tornado.web import RequestHandler
from authlib.jose import jwt, JsonWebKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
from AuthService import settings

DEMO_PRIVATE_KEY = b"""-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,13BD6194E320BA62

xmqgvtCVlG3Y463iCeZt61z3QQwbO+vOMhSr/6NV+7pqYOM+wRy+Dfdb8kBWFNHG
G4Xb9ns61bIOmuOn2OI0UUgIFJpPBor46vaq2MHbIsDKFCHRB740S1VwghX7GSkc
rlra9632cDfCROxaid/1EywkDdC7jwTt9hIGuVfhV9FvDKxjf+pclIi5Be1AQcO/
PFmThKtW0a3LZRJtq61eOnqSzN+1YFxdxKXSZQje4bPmOTzHCDRwcuihFmPDHbj0
+PN2N382AcVUWmKMqfC0bzb1I7rKKVItX6qNyohgFftt+l0GTlFjd4PazciN82t2
HfUmwiJf39jY7i68gBSCUD4vXdz6jPqxVZfHJuXAtIrdSiEFgid6nzLSlbVKbVNa
7t1o78AIikUkf3ohkWglfbqhwvOw8MV073BOIg8kdSocCNS3CEO0yWO0098jaJ+1
005Sb8kl0a3YTTaho2kiUwVIVNeQLwSEF8o98rlSvzaxnJn819tRIJDbhL/LCl5c
2TBNmlX/WulPWO6y33Dy4sKP5jVH8vSg0kNY/St7S5d/hUvkv8W2I30Zj7c7f55d
Woozbv0ouKPpCrbm6q/PqseT+dYkUNq2NyQdReevnNMh6p7CjpCW4Uc/YliqbEwe
H3KEXO5GLhINfIdJWX1OxEjufLA/0xx4K1vvtau+JBDwjtcOENEb9V0OUUQvNnJU
sXM1nqbNzT8yyA0g9D90qtaCPWvaIvgeJp/YSO7VlDiJyFIaIePx8CdbbgX8ozwL
8dwCGZnCNYgtDTnBshPHEoDtf2BmEcb+rfyK0HFUiSke4NPhow9lYmVinyg37mi0
B0jVCQ1T/9fyoOuLxWviNTLtogmLW7JXCAXPRizGAscCjbJxTnZB4KpKsBgyAHb8
FY9WiPuJuiEbD10uaE6sFZlV6LjEiCXkprECviLw+H6JuxC+CLpvf36WHNCmJLaO
pptZLHVGy7VnZB0YPkF4htH31H9gEft56vOs6sHshN4SSIOAw9c6YaIqxcdqJAVG
oECBUFZ0a8s85vPntcrPKT4z8OLrLSmbWtb4BvQPnVfkR6fMdQZ9sG8emOoljYfZ
u2DZAG1IjA5BRcJmMk/ypgSHjSVgKSrXjtPAKENP8LCx7+7N6jzZWEGmxy4p04l9
B8CrG+ry15zH40WzqCTbK9zifV3ZFR2rWbm1+dRclnmKyWhZLxLrzDnLKLXYFnwF
I09Nava4o4pweZk/7IqCmPOckpZDdpOevxplda1A5fyEAirJS5Qn3lQ5Y7dp2AFS
pvRl5QuL7YN8CyLWa6YC74IhvmLixW/IjDIsbcjurkycwNGvtbge8gToiOoT9RlU
Rlvb+mahw/IzSLfI9rqscC6nO0yJMs3b5Z+N46AjKAHjmLoHrj7+e3ojTAXOPj1q
aZlVkM6pXrhcWJYSCQPz8uWT1NJQ4B3y0AMgNAjzLkZpbklzk2coDwGfksrhWEcA
t1R7g4yk/MhPqrWC11nAXbBYekGXAfTelb1op4BpWUm8M8loMS07b0iewbv7b7Qu
mJePXud/3APBaMfT6UtUc4bcZ/rcb/f/8Jx+XJ67dQDHpljDSLAUkA==
-----END RSA PRIVATE KEY-----"""


DEMO_PUBLIC_KEY = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAv72+gVf0TBdfuFck8Pmw
/DMKzkk9bqOoJpIFhZo/sYtF4PT/wfpku4IlNNwrHKhT0MtKHYlM7tMNbgTs810x
fBSTtFTizbp5SbI7KTGoVjtVPC8CxxC30fGsTWagURBpvDFyTnW0oU9hVGyLFTwf
f/u7dgp9iek2gzhJgPEV8NsLdgo+1DapDJXapdGtGE8rxPSnMM/mBruMhOnfO1UP
lkh602JKRpP6EEeOaHIhGMWuIEeDEh9RvH+qXhe7BL5h9ockdhSouzKk5fl/BUr1
2/zO5fevd+5t/MUrAIdhgsSzBkFAvX7Gn/+ObNYvPPYykUXn9/BhAjrQI3tYYjQ3
IQIDAQAB
-----END PUBLIC KEY-----"""


class PublicKeyHandler(RequestHandler):
    def get(self):
        key_data = DEMO_PUBLIC_KEY
        # key = JsonWebKey.import_key(key_data, {'kty': 'RSA'})
        #
        # self.write(key.as_json())
        self.write(key_data)


class AuthHandler(RequestHandler):
    DEMO_CLIENT_ID = 1
    DEMO_CLIENT_SECRET = 'secret'

    def get_valid_client_secret(self, client_id):
        # TODO: replace with a database query
        client_id_to_secret = {
            self.DEMO_CLIENT_ID: self.DEMO_CLIENT_SECRET
        }
        return client_id_to_secret.get(client_id)

    def get_client_authorized_scopes(self, client_id):
        # TODO: replace with DB query to get client's scopes
        scopes = ['example_action:example_resource']
        return ' '.join(scopes)

    def return_jwt(self, client_id):
        scopes = self.get_client_authorized_scopes(client_id)
        header = {'alg': 'RS256', 'typ': 'JWT'}
        payload = {
            'iss': f"https://{settings.AUTH_SERVICE_DOMAIN}/",
            'sub': '123',
            'scope': scopes
        }
        key = load_pem_private_key(DEMO_PRIVATE_KEY, password=b'demo_key', backend=default_backend())
        access_token = jwt.encode(header, payload, key)
        self.set_status(200)
        self.write({
            'access_token': access_token.decode('ascii'),
            'token_type': 'Bearer',
            'expires_in': 'TODO'
        })

    def post(self):
        try:
            request_body = json.loads(self.request.body)
            audience = request_body['audience']
            grant_type = request_body['grant_type']
            client_id = request_body['client_id']
            client_secret = request_body['client_secret']
        except KeyError:
            self.set_status(400, 'Bad request body (missing required field)')
            return
        valid_client_secret = self.get_valid_client_secret(client_id)
        if valid_client_secret and client_secret == valid_client_secret:
            self.return_jwt(client_id)
        else:
            self.set_status(403)
