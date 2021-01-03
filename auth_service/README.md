# wu-labs-auth-service

## Running locally
```shell script
cp packaging/environment/env.dev.example .env
# Fill in the missing values
docker-compose -f docker-compose-dev.yml up --build
```

The application will then be accessible at localhost:8888


## Example usage 

Usage of the auth service to protect endpoints can be found in the src/AuthService/demo/views directory.

These demo URLs are:
* localhost:8888/oauth/token
  * This URL accepts POST requests with the following body:
  `{
        "audience": "value",
        "grant_type": "value",
        "client_id": 1,
        "client_secret": "secret"
    }`
  * The response will return an access token
* localhost:8888/auth-demo
  * This url accepts GET requests and enforces authentication
  * The access token must be present as a bearer token in the Authorization header in order to successfully make a request to this URL
* localhost:8888/scopes-demo
  * This url accepts GET requests, enforces authentication, and provides an example of using the scopes in a JWT to limit access to a resource
