from tornado import httputil

from helpers.requests import RequestsHelper
from utils.multi_dict import MultiDict


class HandlersHelper:
    """
    Provides helper functionalities for request handlers.
    """

    @classmethod
    def build_request_form(
            cls, request: httputil.HTTPServerRequest, form_class, **form_kwargs
    ):
        """
        Builds a form instance with the data in request body.

        Arguments:
            request (tornado.httputil.HTTPServerRequest: The request to build
            form from.
            form_class (class): The class to be instantiated.
            form_kwargs (dict): Keyword arguments to send to form class while
                instantiation.
        Returns:
            form (form_class): An instance of form_class with the body data
            in the request.
        """

        request_form_data = RequestsHelper.get_decoded_body_arguments(request)

        return form_class(formdata=MultiDict(request_form_data), **form_kwargs)
