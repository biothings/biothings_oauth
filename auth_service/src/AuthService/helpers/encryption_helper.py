import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key
)

from AuthService import settings


class EncryptionHelper:
    """
    Contains helper functionalities for encrypting/decrypting data.
    """

    _private_key = load_pem_private_key(
        settings.PRIVATE_KEY.encode("utf-8"),
        password=None,
        backend=default_backend()
    )

    _public_key = load_pem_public_key(
        settings.PUBLIC_KEY.encode("utf-8"),
        backend=default_backend()
    )

    @classmethod
    def encrypt_str(cls, s):
        """
        Encrypts a given string using public key and returning the result as a
        base64 string. The given string is UTF-8 encoded before encrypting.

        :param s: String to be encrypted.
        :return: Encrypted string.
        """

        return base64.b64encode(
            cls._public_key.encrypt(
                s.encode("utf-8"),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        ).decode("UTF-8")

    @classmethod
    def decrypt_str(cls, s):
        """
        Decrypts a given string using private key and returning the result as a
        string. The given string is UTF-8 encoded before decrypting.

        :param s: String to be encrypted.
        :return: Encrypted string.
        """
        return cls._private_key.decrypt(
            base64.b64decode(s.encode("UTF-8")),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode("UTF-8")
