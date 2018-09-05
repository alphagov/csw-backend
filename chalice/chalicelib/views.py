import os
# from urllib.parse import urlparse, parse_qs
from jinja2 import Environment as Jinja2Environment, FileSystemLoader, select_autoescape
# from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import AssetsExtension

# assets_env = AssetsEnvironment('./assets', '/assets')
# env.assets_environment = assets_env


class TemplateHandler:

    def __init__(self, auth):

        self.auth = auth
        self.base_dir = os.getcwd()
        self.template_dir = os.path.join(self.base_dir, 'chalicelib', 'templates')
        self.govuk_dir = os.path.join(self.template_dir, 'govuk-frontend')

        self.env = Jinja2Environment(
            loader=FileSystemLoader([
                self.template_dir,
                self.govuk_dir
            ]),
            autoescape=select_autoescape(['html', 'xml']),
            extensions=[AssetsExtension]
        )

        self.logged_in = False
        self.login_data = {}
        self.route_templates = {
            "/": "logged_in.html",
            "/audit": "audit_list.html",
            "/audit/{id}": "audit.html"
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

    def render_authorized_route_template(self, route, req, data={}):

        try:

            headers = {
                "Content-Type": "text/html"
            }

            auth = self.get_auth_handler()

            self.request_url = auth.get_request_url(req)

            if self.request_url.find('localhost') != -1:

                self.auth_flow = auth.get_auth_flow(self.request_url + route)

                login_url = self.auth_flow.authorization_url()

                logged_in = self.auth.try_login(req)
            else:
                logged_in = True

            # if there is a user then show the requested route
            # TODO add permission control
            if logged_in:

                template_file = self.get_route_template_file(route)

                if self.auth.cookie is not None:
                    login_data = self.auth.get_login_data()
                    data["email"] = login_data["email"]
                    data["token"] = login_data["token"]
                    headers["Set-Cookie"] = self.auth.cookie

            else:

                template_file = 'logged_out.html'

                login_url, _ = self.auth_flow.authorization_url()
                print(login_url)

                data["login_url"] = login_url

            data["asset_path"] = "/assets"

            response_body = self.render_template(template_file, data)
        except Exception as err:
            response_body = "Error text: {0}".format(err)

        return {
            "body": response_body,
            "headers": headers
        }
