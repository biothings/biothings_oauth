from tornado import httputil

from helpers.requests import RequestsHelper
from utils.multi_dict import MultiDict


class HandlersHelper:
    """
    Provides helper functionalities for request handlers.
    """

    @classmethod
    def build_request_form(
            cls, request: httputil.HTTPServerRequest, form_class
    ):
        """
        Builds a form instance with the data in request body.

        Arguments:
            request (tornado.httputil.HTTPServerRequest: The request to build
            form from.
            form_class (class): The class to be instantiated.

        Returns:
            form (form_class): An instance of form_class with the body data
            in the request.
        """

        request_form_data = RequestsHelper.get_decoded_body_arguments(request)

        return form_class(MultiDict(request_form_data))
