import os
import re
import datetime
from http import cookies
import jwt
import json
import google_auth_oauthlib.flow
from chalicelib.aws.gds_secrets_manager_client import GdsSecretsManagerClient


class AuthHandler:

    def __init__(self, app):
        self.app = app

        # TODO get this from AWS secret manager and move into a class method in auth
        self.cookie_expiration = datetime.timedelta(days=1)

        if 'CSW_ENV' in os.environ:
            secrets = GdsSecretsManagerClient(self.app)
            # secrets = Secrets()
            self.csw_secrets = json.loads(secrets.get_secret_value(os.environ['CSW_ENV']))

            self.token_secret = self.csw_secrets['token_secret']
            self.client_config = secrets.parse_escaped_json_secret(self.csw_secrets['google_auth'])

        self.flow = None
        self.token_algorithm = 'HS256'

        self.scopes = [
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/plus.me",
            "https://www.googleapis.com/auth/userinfo.email"
        ]

        self.user_info = "https://www.googleapis.com/oauth2/v2/userinfo?fields=email"
        self.cookie = None
        self.logged_in = False
        self.login_data = {}

    def get_auth_flow(self, url):

        if self.flow is None:

            self.flow = google_auth_oauthlib.flow.Flow.from_client_config(self.client_config, self.scopes)
            self.flow.redirect_uri = url

        return self.flow

    def get_request_url(self, request):

        protocol = 'http'
        if 'X-Forwarded-Proto' in request.headers:
            protocol = request.headers['X-Forwarded-Proto']
        return protocol + "://" + request.headers['Host'] + "/app"

    def get_user_token(self, request):

        cookie = cookies.SimpleCookie()
        cookie.load(request.headers["cookie"])
        token = cookie["session"].value
        return token

    def get_cookie_value(self, req, cookie_name):

        value = None

        if "cookie" in req.headers:

            cookie = cookies.SimpleCookie()
            cookie.load(req.headers["cookie"])
            if cookie_name in cookie:
                value = cookie[cookie_name].value

        return value

    def read_jwt(self, user_jwt):

        user = None

        self.app.log.debug('jwt: ' + user_jwt)

        if (user_jwt is not None):
            user = jwt.decode(user_jwt.encode(), self.token_secret, algorithms=[self.token_algorithm])

            self.app.log.debug('user data: ' + str(user))

        return user

    def has_valid_user(self, req):
        # TODO: There should be a list of valid sessions stored somewhere and
        # TODO: the session ID should be checked against that.  For now it just makes sure
        # TODO: there is a session cookie at all set by this domain.  Not very secure.
        user = None

        if "cookie" in req.headers:

            user_jwt = self.get_cookie_value(req, "session")

            if user_jwt is not None:
                user = self.read_jwt(user_jwt)

        return user

    # Generate a cookie header value
    def generate_cookie_header_val(self, token):

        cookie = cookies.SimpleCookie()
        cookie["session"] = token
        expiration = datetime.datetime.now() + self.cookie_expiration
        cookie["session"]["expires"] = expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
        cookie["session"]["path"] = "/"

        # Workaround the fact that cookie.output returns a string like: 'Set-Cookie: session=650406237; etc..'
        # but we don't want the 'Set-Cookie: ' part in the actual header.
        raw_cookie_output = cookie.output()
        cookie_val = raw_cookie_output.replace("Set-Cookie: ", "")

        return cookie_val

    def generate_logout_header_val(self):

        cookie = cookies.SimpleCookie()
        cookie["session"] = None
        expiration = datetime.datetime.now()
        cookie["session"]["expires"] = expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
        cookie["session"]["path"] = "/"

        # Workaround the fact that cookie.output returns a string like: 'Set-Cookie: session=650406237; etc..'
        # but we don't want the 'Set-Cookie: ' part in the actual header.
        raw_cookie_output = cookie.output()
        cookie_val = raw_cookie_output.replace("Set-Cookie: ", "")

        return cookie_val

    def get_user_from_code(self, url, code):

        flow = self.get_auth_flow(url)

        self.app.log.debug("get_credentials_from_code: got flow")

        self.app.log.debug("request context: " + str(self.app.current_request.context))

        self.google_token = flow.fetch_token(code=code)

        self.app.log.debug("get_credentials_from_code: got token: " + str(self.google_token))

        self.session = flow.authorized_session()

        self.user_data = self.session.get('https://www.googleapis.com/userinfo/v2/me').json()

        self.user = json.dumps(self.user_data)

        return self.user

    def get_jwt(self, user):

        user_jwt = jwt.encode(json.loads(user), self.token_secret, algorithm=self.token_algorithm).decode('utf-8')
        return user_jwt

    def try_login(self, req):

        try:
            self.user_data = self.has_valid_user(req)

            if self.user_data is not None:

                self.app.log.debug('request user is set')

                self.token = self.get_user_token(req)
                self.logged_in = True

            else:

                self.app.log.debug('no user check for code param')

                if "code" in req.query_params:

                    self.app.log.debug('')
                    url = self.get_request_url(req)
                    code = req.query_params["code"]

                    self.app.log.debug(f"code: {code}")

                    self.user = self.get_user_from_code(url, code)

                    # Make sure the email Google OAuthed is on the GDS domain
                    if re.search("digital\.cabinet-office\.gov\.uk", self.user_data['email']):

                        self.user_jwt = self.get_jwt(self.user)

                        self.cookie = self.generate_cookie_header_val(self.user_jwt)

                        self.token = self.google_token

                        self.logged_in = True

                    else:
                        self.app.log.debug(json.dumps(self.user_data))
                        self.logged_in = False
                else:
                    self.logged_in = False

            if self.logged_in:
                self.login_data.update(self.user_data)
                self.login_data["cookie"] = self.cookie
                self.login_data["token"] = self.token

        except Exception as err:
            self.app.log.debug(str(err))
            self.login_data["cookie"] = None
            self.login_data["message"] = "Login failed"
            self.logged_in = False

        return self.logged_in

    def get_login_data(self):
        return self.login_data
