from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler
from jose import jwt
from AuthService import settings


AUTH_SERVICE_DOMAIN = settings.AUTH_SERVICE_DOMAIN
API_AUDIENCE = 'test' #YOUR_API_AUDIENCE
ALGORITHMS = ["RS256"]
PROTOCOL = 'http' if settings.DEBUG else 'https'


class AuthorizedRequestHandler(RequestHandler):
    def get_token_auth_header(self):
        """Obtains the Access Token from the Authorization Header
        """
        auth = self.request.headers.get("Authorization", None)
        if not auth:
            self.set_status(401, 'Authorization header is expected')
            self.finish()
            return

        parts = auth.split()
        status_message = None
        if parts[0].lower() != "bearer":
            status_message = 'Authorization header must start with Bearer'
        elif len(parts) == 1:
            status_message = 'Token not found'
        elif len(parts) > 2:
            status_message = 'Authorization header must be Bearer token'
        if status_message:
            self.set_status(401, status_message)
            self.finish()
            return
        token = parts[1]
        return token

    async def prepare(self):
        token = self.get_token_auth_header()
        client = AsyncHTTPClient()
        response = await client.fetch(f"{PROTOCOL}://{AUTH_SERVICE_DOMAIN}/.well-known/public-key", method="GET")
        public_key = response.body

        status_message = None
        if public_key:
            try:
                payload = jwt.decode(
                    token,
                    public_key.decode('ascii'),
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer="https://" + AUTH_SERVICE_DOMAIN + "/"
                )
            except jwt.ExpiredSignatureError:
                status_message = "Token is expired"
            except jwt.JWTClaimsError:
                status_message = 'Incorrect claims, please check the audience and issuer'
            except Exception as e:
                status_message = 'Unable to parse authentication token'
            if status_message:
                self.set_status(401, status_message)
                self.finish()
                return
            return payload
        self.set_status(401, 'Unable to find appropriate key')
        self.finish()

    def requires_scope(self, required_scope):
        """Determines if the required scope is present in the Access Token
        Args:
            required_scope (str): The scope required to access the resource
        """
        token = self.get_token_auth_header()
        unverified_claims = jwt.get_unverified_claims(token)
        if unverified_claims.get("scope"):
            token_scopes = unverified_claims["scope"].split()
            for token_scope in token_scopes:
                if token_scope == required_scope:
                    return True
        return False


class ExampleAuthRequiredHandler(AuthorizedRequestHandler):
    def get(self):
        self.write("Success")


class ExampleScopeRequiredHandler(AuthorizedRequestHandler):
    def get(self):
        if self.requires_scope("example_action:example_resource"):
            response = "Hello from a private endpoint! You need to be authenticated and have a scope of example_action:example_resource to see this."
            self.write(response)
            self.finish()
        self.set_status(403, "You don't have access to this resource")
        self.finish()
