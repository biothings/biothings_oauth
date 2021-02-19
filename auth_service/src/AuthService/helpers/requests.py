from tornado import httputil


class RequestsHelper:
    """
    Provides helper functionalities for handling requests.
    """

    @classmethod
    def get_decoded_body_arguments(cls, request: httputil.HTTPServerRequest):
        """
        Returns a dictionary containing decoded body arguments as strings.
        (UTF-8).

        Arguments:
            request (tornado.httputil.HTTPServerRequest: The request to decode
            body arguments from.

        Returns:
            (dict): Decoded body arguments dictionary.
        """
        return {
            key: [list_item.decode("UTF-8") for list_item in value]
            for key, value in request.body_arguments.items()
        }
