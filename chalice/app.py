"""
OOP-approach for more flexibility and redabiilty.
First specialise the Chalice class,
then instantiate and initialize its app object,
and finally import all views (routes and lambdas).
"""

import importlib
import logging
import os

from chalice import Chalice

from chalicelib.auth import AuthHandler
from chalicelib.template_handler import TemplateHandler
from chalicelib.utilities import Utilities


class CloudSecurityWatch(Chalice):
    """
    Concrete child of Chalice giving us the opportunity to
    overload any method, add new ones (as well as class/instance vars),
    and use mixin classes, e.g. for auth, templating and logging.
    """

    def __call__(self, event, context):
        """
        Executes every time the Chalice object is called,
        e.g. a route is dispatched and I guess a lambda triggered.
        Overloaded to log its params and response as a proof of concept.
        """
        self.log.debug('EVENT = ' + str(event))
        # TODO: Verify that all this must occure every time a route decorated function is called.
        # if load_route_services:
        #     self.log.debug('Loading route services')
        #     try:
        #         self.auth = AuthHandler(self)
        #         self.log.debug("Loaded auth")
        #         self.templates = TemplateHandler(self)
        #         self.log.debug("Loaded templates")
        #         self.api.binary_types = [
        #             "application/octet-stream",
        #             "image/webp",
        #             "image/apng",
        #             "image/png",
        #             "image/svg",
        #             "image/jpeg",
        #             "image/x-icon",
        #             "image/vnd.microsoft.icon",
        #             "application/x-font-woff",
        #             "font/woff",
        #             "font/woff2",
        #             "font/eot"
        #         ]
        #     except Exception as err:
        #         self.log.error('LOAD ROUTE SERVICES: ' + str(err))
        return super(CloudSecurityWatch, self).__call__(event, context)

    def route(self, path, **kwargs):
        """
        Executes once per route added in a Chalice objects.
        Pre/post-adding hooks as the decorator above for route method.
        !!! ALWAYS !!! pop non-chalice keyword arguments before the super,
        otherwise a nasty exception will be raised (chalice/app.py line 617).
        """
        # add code here to execute before the route is dict is updated
        view_func = super(CloudSecurityWatch, self).route(path, **kwargs)
        # add code here to execute after the route is dict is updated
        return view_func

    def load_views(self, views_list):  # TODO: include/exclude modules/views
        """
        load (import) all views
        this looks a cyclical import,
        but it is the way all Flask-clones can be structured
        """
        for view in views_list:
            importlib.import_module('chalicelib.' + view)


# TODO: Use the overloaded __call__ or route for this
def load_route_services():

    app.log.debug('Loading route services')

    try:
        app.auth = AuthHandler(app)

        app.log.debug("Loaded auth")

        app.templates = TemplateHandler(app)

        app.log.debug("Loaded templates")

        app.api.binary_types = [
            "application/octet-stream",
            "image/webp",
            "image/apng",
            "image/png",
            "image/svg",
            "image/jpeg",
            "image/x-icon",
            "image/vnd.microsoft.icon",
            "application/x-font-woff",
            "font/woff",
            "font/woff2",
            "font/eot"
        ]

    except Exception as err:
        app.log.error(str(err))


def read_asset(proxy):

    binary_types = app.api.binary_types

    ascii_types = [
        "text/plain",
        "text/css",
        "text/javascript"
    ]

    true_path = os.path.join(os.path.dirname(__file__), 'chalicelib', 'assets', proxy)
    app.log.debug(true_path)

    if ".." in proxy:
        raise Exception(f"No back (..) navigating: {proxy}")

    mime_type = app.utilities.get_mime_type(true_path)

    if mime_type in ascii_types:
        with open(true_path, 'r') as text:
            data = text.read()
    elif mime_type in binary_types:
        with open(true_path, 'rb') as img:
            data = img.read()
    else:
        raise Exception(f"Unsupported file type: {mime_type}")

    return data


# Instantiate and initialise the Chalice child object
app = CloudSecurityWatch(app_name='cloud-security-watch')
# switch debug logging on
app.log.setLevel(logging.DEBUG)
app.prefix = os.environ["CSW_PREFIX"]
app.utilities = Utilities()
# load decorated function-based views from another chalicelib file
app.load_views(['routes', 'views', ])
