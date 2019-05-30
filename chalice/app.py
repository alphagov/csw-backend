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
        return super(CloudSecurityWatch, self).__call__(event, context)

    def route(self, path, **kwargs):
        """
        Executes once per route added in a Chalice objects.
        Pre/post-adding hooks as the decorator above for route method.
        !!! ALWAYS !!! pop non-chalice keyword arguments before the super,
        otherwise a nasty exception will be raised (chalice/app.py line 617).
        """
        return super(CloudSecurityWatch, self).route(path, **kwargs)

    def lambda_function(self, name=None):
        """
        Same as route above but for the generic lambdas.
        """
        return super(CloudSecurityWatch, self).lambda_function(name)

    def load_views(self, views_list):  # TODO: include/exclude modules/views
        """
        load (import) all views
        this looks a cyclical import,
        but it is the way all Flask-clones can be structured
        """
        this = importlib.import_module(
            "app"
        )  # obtain a reference to this module (app.py)
        for (
            view
        ) in (
            views_list
        ):  # iterate over all the filenames passed with this function call
            module = importlib.import_module(
                "chalicelib." + view
            )  # keep a reference to each module we iterate
            for obj in dir(
                module
            ):  # iterate the names of every definition inside the itarated module
                obj_ref = getattr(
                    module, obj
                )  # store a reference to the itarated names
                if callable(
                    obj_ref
                ):  # and finally if it the definition is a function...
                    setattr(
                        this, obj, obj_ref
                    )  # make that function an attribute of the app module too


# TODO: Use the overloaded __call__ or route for this
def load_route_services():
    # This can't be imported until after app is declared
    from chalicelib.auth import AuthHandler
    from chalicelib.template_handler import TemplateHandler

    app.log.debug("Loading route services")

    try:
        app.auth = AuthHandler(app)
        app.auth.get_params()
        app.auth.initialise_flow(app.current_request)

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
            "font/eot",
        ]

        # Define a list of routes which can be rendered outside login
        # TODO - Find a nicer way of doing this per route.
        app.templates.set_logged_out_routes(["", "/", "/login", "/logout", "/denied"])

    except Exception as err:
        app.log.error(str(err))


def read_asset(proxy):

    binary_types = app.api.binary_types

    ascii_types = ["text/plain", "text/css", "text/javascript"]

    true_path = os.path.join(os.path.dirname(__file__), "chalicelib", "assets", proxy)
    app.log.debug(true_path)

    if ".." in proxy:
        raise Exception(f"No back (..) navigating: {proxy}")

    mime_type = app.utilities.get_mime_type(true_path)

    if mime_type in ascii_types:
        with open(true_path, "r") as text:
            data = text.read()
    elif mime_type in binary_types:
        with open(true_path, "rb") as img:
            data = img.read()
    else:
        raise Exception(f"Unsupported file type: {mime_type}")

    return data


# Instantiate and initialise the Chalice child object
app = CloudSecurityWatch(app_name="cloud-security-watch")

# switch debug logging on
app.log.setLevel(logging.DEBUG)
app.prefix = os.environ["CSW_PREFIX"]
app.env = os.environ["CSW_ENV"]
app.utilities = Utilities()
# load decorated function-based views from another chalicelib file
# TODO: Replace load_views with a django-like dispatcher...
# TODO: ... with the additional functionality fo binding periodic and triggered lambdas.
app.load_views(
    [
        "routes",
        "demos",  # route lambdas (aka HTTP responses, views)
        "admin",
        "audit",  # periodic and triggered lambdas
        "api",  #
    ]
)
