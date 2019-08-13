import os
import re
import datetime

# from urllib.parse import urlparse, parse_qs
from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateHandler:
    """
    This class implements the jinja2 template loading and rendering.

    It also populates default variables required by all templates
    like the asset path.

    As part of the above it creates the top level menu which needs
    moving somewhere else.

    It invokes the AuthHandler class (from self.app.auth) to wrap
    requests to render a template with some authorisation logic
    and renders a denied template on failure.

    This is a bit tightly coupled and could do with a re-write to
    separate out the duties of each class.
    """

    def __init__(self, app):

        self.app = app
        self.auth = app.auth

        self.base_dir = os.getcwd()
        self.template_dir = os.path.join(self.base_dir, "chalicelib", "templates")
        self.govuk_dir = os.path.join(self.template_dir, "govuk-frontend")

        self.env = Environment(
            loader=FileSystemLoader([self.template_dir, self.govuk_dir]),
            autoescape=select_autoescape(["html", "xml"]),
        )

        self.register_filters()

        self.logged_in = False
        self.login_data = {}

    def set_logged_out_routes(self, routes_list):
        self.logged_out_routes = routes_list

    def render_template(self, file, params):

        template = self.get_template(file)
        body = template.render(**params)
        return body

    def get_request_path(self):

        self.base_url = self.auth.get_base_url(self.app.current_request)

        # self.app.log.debug("Headers: " + str(self.app.current_request.headers))
        # self.app.log.debug("Context: " + str(self.app.current_request.context))
        # return self.app.current_request.context['resourcePath']
        full_path = self.app.current_request.context["path"]
        base_path = self.get_root_path()
        path = full_path.replace(base_path, "")
        return path

    def get_template(self, file):

        try:
            template = self.env.get_template(file)
        except Exception as err:
            template = None
            self.app.log.debug("Tried to load non-existent template: " + str(err))
        return template

    def get_auth_handler(self):

        return self.auth

    def render_parameterized_message(self, message, params):
        return message.format(*params)

    def register_filters(self):
        def format_datetime(value, format="datetime"):
            """
            Format python datetime types into strings
            """
            if format == "datetime":
                render_as = value.strftime("%d/%m/%Y %H:%M")
            elif format == "date":
                render_as = value.strftime("%d/%m/%Y")
            elif format == "time":
                render_as = value.strftime("%H:%M")

            return render_as

        self.env.filters["datetime"] = format_datetime

        def format_aws_account_id(value):
            """
            Add leading 0s to fixed length AWS account IDs
            """
            return str(value).zfill(12)

        self.env.filters["aws_account_id"] = format_aws_account_id

        def format_timestamp(value, format="datetime"):
            """
            Format string literal timestamp into datetime values
            """

            timestamp_pattern = "^(\d+)-(\d+)-(\d+)\s(\d+):(\d+).+$"

            m = re.search(timestamp_pattern, value)

            if format == "datetime":
                render_as = (
                    m.group(3)
                    + "/"
                    + m.group(2)
                    + "/"
                    + m.group(1)
                    + " "
                    + m.group(4)
                    + ":"
                    + m.group(5)
                )
            elif format == "date":
                render_as = m.group(3) + "/" + m.group(2) + "/" + m.group(1)
            elif format == "time":
                render_as = m.group(4) + ":" + m.group(5)

            return render_as

        self.env.filters["timestamp"] = format_timestamp

    def is_real(self):
        return (self.base_url.find("localhost") == -1) and (
            self.base_url.find("127.0.0.1") == -1
        )

    def get_menu_active_class_modifier(self, route, test):
        return "--active" if route == test else ""

    def get_menu(self, root_path=""):

        route = self.get_request_path()

        return [
            # {
            #     "name": "Overview",
            #     "link": f"{root_path}/overview",
            #     "active": re.match("^\/overview", route),
            # },
            {
                "name": "Statistics",
                "link": f"{root_path}/statistics",
                "active": re.match("^\/statistics", route),
            },
            {
                "name": "My teams",
                "link": f"{root_path}/team",
                "active": re.match("^\/team", route),
            },
            {
                "name": "My exceptions",
                "link": f"{root_path}/exception",
                "active": re.match("^\/exception", route),
            },
        ]

    def refuse(self, req, type, item):
        response = self.render_authorized_template(
            "denied.html", req, {"refused": {"type": type, "item": item}}
        )
        return response

    def get_redirect_status(self, req):
        """
        Decides whether a login redirect is required or completed
        If a user goes straight to a page which requires login but does not have a valid JWT
        - the requested path is stored in a login_redirect cookie
        - the user is redirected to the denied page to login
        - the OAuth process returns the user to the home page
        - if the cookie is set
                and the user is logged in
            the home page redirects to the cookie path
        - if the cookie is present
                and the user is logged in
                and the requested page matches the cookie path
            the cookie is expired
        """
        route = self.get_request_path()
        self.app.log.debug(f"Check redirect status for: {route}")
        login_redirect = self.auth.get_cookie_value(req, "login_redirect")
        status = {"action": "none"}
        has_header = login_redirect not in [None, ""]
        is_current_route = login_redirect == route
        is_after_oauth_route = route == self.auth.get_after_oauth_path()

        if has_header:
            status = {"action": "notify", "target": login_redirect}

        if has_header and is_after_oauth_route:
            status = {"action": "redirect", "target": login_redirect}

        if has_header and is_current_route:
            status = {"action": "complete"}

        self.app.log.debug("Redirect Status: " + str(status))
        return status

    def render_authorized_template(
        self, template_file, req, data=None, check_access=[]
    ):
        """
        Check the user is logged in
        If so render the template using the data supplied
        If not create a redirect to force login
        Optionally check whether the user has access to a given list of resources
        by calling the user_has_access method in each item
        TODO make the access check generic
        :param template_file:
        :param req:
        :param data:
        :param team:
        :return:
        """

        headers = {"Content-Type": "text/html"}

        try:

            # If no template data has been passed initialise an empty dict
            if data is None:
                data = {}

            status_code = 200

            route = self.get_request_path()

            self.base_url = self.auth.get_base_url(req)

            self.app.log.debug("Base URL: " + self.base_url)

            if self.is_real():

                root_path = self.auth.get_interface_root_path(req)

                logged_in = self.auth.try_login(req)

                self.app.log.debug("Not localhost")
            else:
                logged_in = True
                root_path = ""
                data["name"] = "[User]"

                self.app.log.debug("Is localhost")

            asset_path = f"{root_path}/assets"

            if template_file == "logged_out.html":

                logged_in = False
                headers["Set-Cookie"] = self.auth.generate_logout_header_val()

            # if there is a user then show the requested route
            # TODO add permission control
            login_data = self.auth.get_login_data()

            # check for login_redirect in cookie
            redirect_status = self.get_redirect_status(req)

            # Successfully authenticated and permissioned user
            if logged_in:

                has_access = True
                if len(check_access) > 0:
                    user = self.auth.get_user_record(login_data["email"])
                    for item in check_access:
                        item_access = item.user_has_access(user)
                        if not item_access:
                            refused = item.get_item()

                    has_access = has_access & item_access

                if has_access:
                    data.update(login_data)

                    self.app.log.debug("template data: " + str(data))

                    if self.auth.cookie is not None:
                        headers["Set-Cookie"] = self.auth.cookie

                    # Set redirect header
                    if redirect_status["action"] == "redirect":
                        # Redirect based on cookie
                        target = redirect_status["target"]
                        self.app.log.debug(f"Redirect to target: {target}")
                        status_code = 302
                        headers["Location"] = root_path + target
                    elif (
                        "default_redirect" in data and data["default_redirect"] != route
                    ):
                        # Redirect to default after login target
                        target = data["default_redirect"]
                        self.app.log.debug(f"Redirect to target: {target}")
                        status_code = 302
                        headers["Location"] = root_path + target

                    # Unset redirect cookie
                    if redirect_status["action"] == "complete":
                        self.app.log.debug("Redirection made - deleting cookie")
                        expiration = datetime.datetime.now()
                        headers["Set-Cookie"] = self.auth.create_set_cookie_header(
                            "login_redirect", "", expiration
                        )

                    data["logout_url"] = f"{root_path}/logout"
                    data["menu"] = self.get_menu(root_path)
                else:
                    template_file = "denied.html"

                    data = {"refused": {"type": "team", "item": refused}}

            # Check for successful auth but non-registered user
            elif login_data["authenticated"] and not login_data["is_registered"]:

                template_file = "request_access.html"

                status_code = 403

            # Back to logged out
            else:
                # Try loading the template matching the route name
                route_template = self.get_template(f"{route}.html")
                if (route in self.logged_out_routes) and (route_template is not None):
                    template_file = f"{route}.html"
                else:
                    # Fallback on the logged_out template
                    template_file = "logged_out.html"

                # Redirect to access denied for login
                if route not in self.logged_out_routes:
                    status_code = 302
                    headers["Location"] = self.base_url + "/denied"
                    # Return user to requested route after login
                    self.app.log.debug(
                        "Not logged in - add login redirect cookie to target: " + route
                    )
                    expiration = self.auth.get_default_cookie_expiration()
                    headers["Set-Cookie"] = self.auth.create_set_cookie_header(
                        "login_redirect", route, expiration
                    )

            # Always populate login link in template data
            login_url = self.auth.get_auth_url(self.base_url + route)

            # Add the redirect path to the template data so
            # you can tell the user they're being redirected
            if redirect_status["action"] == "notify":
                data["login_redirect"] = redirect_status["target"]

            data["route"] = route
            data["login_url"] = login_url
            data["asset_path"] = asset_path
            data["base_path"] = root_path

            # Don't populate back link if it links to the current page.
            # For forms which post to themselves
            if "referer" in req.headers and req.headers["referer"] != (
                self.base_url + route
            ):
                self.app.log.debug(
                    "Backlink: " + req.headers["referer"] + " <> " + route
                )
                data["back_link"] = req.headers["referer"]

            response_body = self.render_template(template_file, data)

        except Exception as err:
            response_body = "Error text: {0}".format(err)

        return {"headers": headers, "body": response_body, "status_code": status_code}

    def get_root_path(self):
        root_path = self.auth.get_root_path(self.app.current_request)

        return root_path

    def default_server_error(
        self, status_code=200, message="Something went wrong."
    ):
        try:
            req = self.app.current_request
            self.base_url = self.auth.get_base_url(req)

            self.app.log.debug("Base URL: " + self.base_url)

            template_file = "server_error.html"
            headers = {"Content-Type": "text/html"}
            root_path = self.get_root_path()
            data = {
                "message": message,
                "base_path": root_path,
                "asset_path": f"{root_path}/assets",
            }
            response_body = self.render_template(template_file, data)
        except Exception as error:
            response_body = str(error)
        return {"headers": headers, "body": response_body, "status_code": status_code}
