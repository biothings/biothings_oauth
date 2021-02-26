from datetime import datetime

from auth.models import (
    Client, ClientType, Api, Scope, User, ClientApi, ClientApiScope, UserRole
)
from AuthService.database import Session
from helpers.models_helpers.client_helper import ClientHelper


DB = Session()


def create_users():
    users = [
        User(
            role=UserRole.ADMIN,
            identity_provider="GITHUB",
            identity_provider_user_id="github_admin_user",
            username="Github-Admin-user",
            last_login=datetime.utcnow()
        ),
        User(
            role=UserRole.ADMIN,
            identity_provider="ORCID",
            identity_provider_user_id="orcid_admin_user",
            username="ORCID-Admin-user",
            last_login=datetime.utcnow()
        ),
        User(
            role=UserRole.REGULAR_USER,
            identity_provider="ORCID",
            identity_provider_user_id="orcid_user",
            username="ORCID-user",
            last_login=datetime.utcnow()
        ),
        User(
            role=UserRole.REGULAR_USER,
            identity_provider="GITHUB",
            identity_provider_user_id="github_user",
            username="GITHUB-user",
            last_login=datetime.utcnow()
        ),
    ]

    for user in users:
        DB.add(user)
    DB.commit()

    return users


def create_clients(users=None):
    if not users:
        users = create_users()

    clients = []
    client_names = ["Chrome", "Firefox", "Safari", "Postman"]
    client_types = [
        ClientType.MACHINE_TO_MACHINE_APP,
        ClientType.NATIVE,
        ClientType.REGULAR_WEB_APP,
        ClientType.SINGLE_PAGE_WEB_APP
    ]

    for i in range(4):
        client = Client(name=client_names[i], type=client_types[i])
        client.user = users[i % 2]

        ClientHelper.set_client_credentials(client)

        clients.append(client)
        DB.add(client)

    DB.commit()

    return clients


def create_apis(clients=None):
    if not clients:
        clients = create_clients()

    api_identifiers = ["users-list", "apps-list", "blogs-list", "ratings-list"]
    api_names = ["Users List", "Apps List", "Blogs List", "Ratings List"]
    apis = []

    for i in range(4):
        api = Api(identifier=api_identifiers[i], name=api_names[i])
        client_api = ClientApi(api=api, client=clients[i])
        api.clients.append(client_api)
        apis.append(api)

        DB.add(api)

    DB.commit()

    return apis


def create_scopes(apis=None):
    if not apis:
        apis = create_apis()

    scope_names = [
        ["add:users", "update:apps", "delete:blogs", "retrieve:ratings"],
        ["update:blogs", "add:ratings"],
        ["update:users", "delete:apps"],
        ["add:non-existing-resource-1", "update:non-existing-resource-2"]
    ]
    for i in range(4):
        for j in range(len(scope_names[i])):
            scope = Scope(name=scope_names[i][j])
            apis[i].scopes.append(scope)

            DB.add(ClientApiScope(scope=scope, client_api=apis[i].clients[0]))

    DB.commit()


if __name__ == '__main__':
    create_scopes()
