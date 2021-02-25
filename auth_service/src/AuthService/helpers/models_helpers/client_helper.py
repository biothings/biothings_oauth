import secrets
import uuid

from helpers.encryption_helper import EncryptionHelper


class ClientHelper:
    """
    Contains helper functionalities for handling Client model instances.
    """

    @classmethod
    def set_client_credentials(cls, client):
        """
        Sets a new client ID and client secret for a Client model instance.

        :param client: Client model instance.
        """

        client.client_id = uuid.uuid4()
        client.client_secret = EncryptionHelper.encrypt_str(
            secrets.token_urlsafe()[:25]
        )
