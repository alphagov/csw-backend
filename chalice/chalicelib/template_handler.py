import os
import re
import datetime
# from urllib.parse import urlparse, parse_qs
from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateHandler:

    def __init__(self, app):

        self.app = app
        self.auth = app.auth

        self.base_dir = os.getcwd()
        self.template_dir = os.path.join(self.base_dir, 'chalicelib', 'templates')
        self.govuk_dir = os.path.join(self.template_dir, 'govuk-frontend')

        self.env = Environment(
            loader=FileSystemLoader([
                self.template_dir,
                self.govuk_dir
            ]),
            autoescape=select_autoescape(['html', 'xml']),
        )

        self.register_filters()

        self.logged_in = False
        self.login_data = {}

    def render_template(self, file, params):

        template = self.get_template(file)
        body = template.render(**params)
        return body

    def get_request_path(self):

        self.base_url = self.auth.get_base_url(self.app.current_request)
        self.app.log.debug("Context: "+str(self.app.current_request.context))
        # return self.app.current_request.context['resourcePath']
        full_path = self.app.current_request.context['path']
        base_path = self.get_root_path()
        path = full_path.replace(base_path,"")
        return path


    def get_template(self, file):

        template = self.env.get_template(file)
        return template

    def get_auth_handler(self):

        return self.auth

    def render_parameterized_message(self, message, params):
        return message.format(*params)

    def register_filters(self):

        def format_datetime(value, format='datetime'):
            if format == 'datetime':
                render_as = value.strftime('%d/%m/%Y %H:%M')
            elif format == 'date':
                render_as = value.strftime('%d/%m/%Y')
            elif format == 'time':
                render_as = value.strftime('%H:%M')

            return render_as

        self.env.filters['datetime'] = format_datetime

        def format_timestamp(value, format='datetime'):

            timestamp_pattern = '^(\d+)-(\d+)-(\d+)\s(\d+):(\d+).+$'

            m = re.search(timestamp_pattern, value)

            if format == 'datetime':
                render_as = m.group(3) + "/" + m.group(2) + "/" + m.group(1) + " " + m.group(4) + ":" + m.group(5)
            elif format == 'date':
                render_as = m.group(3) + "/" + m.group(2) + "/" + m.group(1)
            elif format == 'time':
                render_as = m.group(4) + ":" + m.group(5)

            return render_as

        self.env.filters['timestamp'] = format_datetime

    def is_real(self):
        return ((self.base_url.find('localhost') == -1) and (self.base_url.find('127.0.0.1') == -1))

    def get_menu_active_class_modifier(self, route, test):
        return ('--active' if route == test else '')

    def get_menu(self, root_path=""):

        route = self.get_request_path()

        return [
            {
                "name": "Overview",
                "link": f"{root_path}/overview",
                "active": re.match("^\/overview",route)
            },
            {
                "name": "My teams",
                "link": f"{root_path}/team",
                "active": re.match("^\/team",route)
            }
        ]

    def get_redirect_status(self, req):
        """
        Decides whether a login redirect is required or completed
        :param req:
        :return:
        """
        route = self.get_request_path()
        self.app.log.debug(f"Check redirect status for: {route}")
        login_redirect = self.auth.get_cookie_value(req, "login_redirect")
        status = { "action": "none" }
        has_header = (login_redirect is not None)
        is_current_route = (login_redirect == route)
        is_non_redirected_route = route not in [None,"","/","/logout","/login"]

        if (has_header
                and (not is_current_route)
                and (not is_non_redirected_route)):
            status = {
                "action": "redirect",
                "target": login_redirect
            }

        if (has_header and is_current_route):
            status = {
                "action": "complete"
            }
        self.app.log.debug("Redirect Status: " + str(status))
        return status

    def render_authorized_template(self, template_file, req, data=None):

        headers = {
            "Content-Type": "text/html"
        }

        try:

            # If no template data has been passed initialise an empty dict
            if data is None:
                data = {}

            status_code = 200

            route = self.get_request_path()

            self.base_url = self.auth.get_base_url(req)

            self.app.log.debug('Base URL: ' + self.base_url)

            if self.is_real():

                root_path = "/app"

                logged_in = self.auth.try_login(req)

                self.app.log.debug('Not localhost')
            else:
                logged_in = True
                root_path = ""
                data["name"] = "[User]"

                self.app.log.debug('Is localhost')

            asset_path = f"{root_path}/assets"

            if template_file == 'logged_out.html':

                logged_in = False
                headers["Set-Cookie"] = self.auth.generate_logout_header_val()

            # if there is a user then show the requested route
            # TODO add permission control
            login_data = self.auth.get_login_data()

            # Successfully authenticated and permissioned user
            if logged_in:

                data.update(login_data)

                self.app.log.debug('template data: '+str(data))

                if self.auth.cookie is not None:
                    headers["Set-Cookie"] = self.auth.cookie

                # check for login_redirect in cookie
                redirect_status = self.get_redirect_status(req)

                # unset redirect cookie and set redirect header
                if ((redirect_status["action"] == "redirect")
                    and (redirect_status["target"] != "/logout")):
                    self.app.log.debug("Redirect to target: "+redirect_status["target"])
                    status_code = 302
                    headers["Location"] = root_path + redirect_status["target"]

                if (redirect_status["action"] == "complete"):
                    self.app.log.debug("Redirection made - deleting cookie")
                    expiration = datetime.datetime.now()
                    headers["Set-Cookie"] += self.auth.create_set_cookie_header("login_redirect", "", expiration)

                data["logout_url"] = f"{root_path}/logout"
                data["menu"] = self.get_menu(root_path)

            # Check for successful auth but non-registered user
            elif login_data['authenticated'] and not login_data['is_registered']:

                template_file = 'request_access.html'

                status_code = 403

            # Back to logged out
            else:
                template_file = 'logged_out.html'

                # Redirect to homepage to login
                if route not in ["", "/","/logout"]:
                    status_code = 302
                    headers["Location"] = self.base_url
                    # Store requested path in login_redirect cookie
                    self.app.log.debug("Not logged in - add login redirect cookie to target: "+route)
                    expiration = self.auth.get_default_cookie_expiration()
                    headers["Set-Cookie"] = self.auth.create_set_cookie_header("login_redirect", route, expiration)

            # Always populate login link in template data
            login_url = self.auth.get_auth_url(self.base_url + route)

            data["login_url"] = login_url
            data["asset_path"] = asset_path
            data["base_path"] = root_path

            if "referer" in req.headers:
                data["back_link"] = req.headers['referer']

            response_body = self.render_template(template_file, data)

        except Exception as err:
            response_body = "Error text: {0}".format(err)

        return {
            "headers": headers,
            "body": response_body,
            "status_code": status_code
        }

    def get_root_path(self):
        if self.is_real():
            root_path = "/app"
        else:
            root_path = ""
            self.app.log.debug('Is localhost')

        return root_path

    def default_server_error(self, req, status_code=200, message="Something went wrong."):
        try:
            self.base_url = self.auth.get_base_url(req)

            self.app.log.debug('Base URL: ' + self.base_url)

            template_file = "server_error.html"
            headers = {
                "Content-Type": "text/html"
            }
            root_path = self.get_root_path()
            data = {
                "message": message,
                "base_path": root_path,
                "asset_path": f"{root_path}/assets"
            }
            response_body = self.render_template(template_file, data)
        except Exception as error:
            response_body = str(error)
        return {
            "headers": headers,
            "body": response_body,
            "status_code": status_code
        }
