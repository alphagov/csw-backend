import os
import re
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
        self.route_templates = {
            "/": "logged_in.html",
            "/logout": "logged_out.html",
            "/audit": "audit_list.html",
            "/audit/{id}": "audit.html",
            "/overview": "overview.html",
            "/team": "teams.html",
            "/team/{id}/dashboard": "team_dashboard.html",
            "/overview": "overview.html"
        }

    def get_route_template_file(self, route):
        if route in self.route_templates:
            template_file = self.route_templates[route]
        else:
            template_file = 'logged_in.html'

        return template_file

    def render_template(self, file, params):

        template = self.get_template(file)
        body = template.render(**params)
        return body

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
        return ((self.request_url.find('localhost') == -1) and (self.request_url.find('127.0.0.1') == -1))

    def get_menu_active_class_modifier(self, route, test):
        return ('--active' if route == test else '')

    def get_menu(app, root_path="", route="/"):

        return [
            {
                "name": "Home",
                "link": f"{root_path}",
                "active": ('--active' if route == "/" else '')
            },
            {
                "name": "Overview",
                "link": f"{root_path}/overview",
                "active": ('--active' if re.match("^\/overview",route) else '')
            },
            {
                "name": "Product Teams",
                "link": f"{root_path}/team",
                "active": ('--active' if re.match("^\/team",route) else '')
            }
        ]

    def render_authorized_route_template(self, route, req, data={}):

        try:
            status_code = 200

            headers = {
                "Content-Type": "text/html"
            }

            auth = self.get_auth_handler()

            self.request_url = auth.get_request_url(req)

            self.app.log.debug('Request URL: ' + self.request_url)

            if self.is_real():

                self.auth_flow = auth.get_auth_flow(self.request_url + route)
                root_path = "/app"

                logged_in = self.auth.try_login(req)

                self.app.log.debug('Not localhost')
            else:
                logged_in = True
                root_path = ""
                data["name"] = "[User]"

                self.app.log.debug('Is localhost')

            asset_path = f"{root_path}/assets"
            # if there is a user then show the requested route
            # TODO add permission control
            if route == '/logout':

                logged_in = False
                headers["Set-Cookie"] = self.auth.generate_logout_header_val()

            if logged_in:

                template_file = self.get_route_template_file(route)

                login_data = self.auth.get_login_data()
                data.update(login_data)

                self.app.log.debug('template data: '+str(data))

                if self.auth.cookie is not None:
                    headers["Set-Cookie"] = self.auth.cookie

                data["logout_url"] = f"{root_path}/logout"
                data["menu"] = self.get_menu(root_path, route)

            else:

                template_file = 'logged_out.html'

                login_url, _ = self.auth_flow.authorization_url()

                data["login_url"] = login_url

                # Redirect to homepage to login
                if route != "/":
                    status_code = 302
                    headers["Location"] = self.request_url

            data["asset_path"] = asset_path
            data["base_path"] = root_path

            response_body = self.render_template(template_file, data)

        except Exception as err:
            response_body = "Error text: {0}".format(err)

        return {
            "body": response_body,
            "status_code": status_code,
            "headers": headers
        }
