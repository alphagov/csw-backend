import os
import datetime
import httplib2
from http import cookies
import jwt
import json
import google_auth_oauthlib.flow
from chalicelib.secrets import Secrets


class AuthHandler:

    def __init__(self):

        # TODO get this from AWS secret manager and move into a class method in auth
        self.cookie_expiration = datetime.timedelta(days=1)

        if 'CSW_ENV' in os.environ:
            secrets = Secrets()
            self.csw_secrets = json.loads(secrets.get_secret_value(os.environ['CSW_ENV']))

            self.token_secret = self.csw_secrets['token_secret']
            self.client_config = secrets.parse_escaped_json_secret(self.csw_secrets['google_auth'])

        self.flow = None
        self.token_algorithm = 'HS256'

        self.scopes = [
            "https://www.googleapis.com/auth/plus.login",
            "https://www.googleapis.com/auth/userinfo.email"
        ]

        self.user_info = "https://www.googleapis.com/oauth2/v2/userinfo?fields=email"
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
        return protocol + "://" + request.headers['Host']

    def get_user(self, credentials):

        user = ""

        http = httplib2.Http()
        http = credentials.authorize(http)
        resp, content = http.request(self.user_info)

        if resp.status == 200:
            user = content

        return user

    def get_user_token(self, request):

        cookie = cookies.SimpleCookie()
        cookie.load(request.headers["cookie"])
        token = cookie["session"].value
        return token

    def get_cookie_value(self, req, cookie_name):

        if "cookie" in req.headers:

            cookie = cookies.SimpleCookie()
            cookie.load(req.headers["cookie"])
            value = cookie[cookie_name].value

        else:
            value = None

        return value

    def has_valid_user(self, req):
        # TODO: There should be a list of valid sessions stored somewhere and
        # TODO: the session ID should be checked against that.  For now it just makes sure
        # TODO: there is a session cookie at all set by this domain.  Not very secure.
        user = None

        if "cookie" in req.headers:

            user_jwt = self.get_cookie_value(req, "session")

            user = jwt.decode(user_jwt.encode(), self.token_secret, algorithms=[self.token_algorithm])

        return user

    # Generate a cookie header value
    def generate_cookie_header_val(self, token):

        cookie = cookies.SimpleCookie()
        cookie["session"] = token
        expiration = datetime.now() + self.cookie_expiration
        cookie["session"]["expires"] = expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
        cookie["session"]["path"] = "/"

        # Workaround the fact that cookie.output returns a string like: 'Set-Cookie: session=650406237; etc..'
        # but we don't want the 'Set-Cookie: ' part in the actual header.
        raw_cookie_output = cookie.output()
        cookie_val = raw_cookie_output.replace("Set-Cookie: ", "")

        return cookie_val

    def get_credentials_from_code(self, url, code):

        flow = self.get_auth_flow(url)
        self.google_token = flow.fetch_token(code=code)

        credentials = self.flow.credentials

        return credentials

    def get_jwt(self, user):

        user_jwt = jwt.encode(json.loads(user), self.token_secret, algorithm=self.token_algorithm).decode('utf-8')
        return user_jwt

    def get_user_data(self, user):

        user_data = json.loads(user.decode('utf-8'))
        return user_data

    def try_login(self, req):

        try:
            self.user = self.has_valid_user(req)

            if self.user is not None:
                self.user_data = self.auth.get_user_data(self.user)
                self.token = self.get_user_token(req)

            else:

                code = req.query_params["code"]
                credentials = self.get_credentials_from_code(code)
                self.user = self.get_user(credentials)

                self.user_jwt = self.get_jwt(self.user)

                self.cookie = self.generate_cookie_header_val(self.user_jwt)

                self.user_data = self.get_user_data(self.user)

                self.token = credentials.get_access_token()[0]

                self.login_data["cookie"] = self.cookie
                self.login_data["email"] = self.user_data['email']
                self.login_data["token"] = self.token
                self.login_data["asset_path"] = "/api/assets"

                self.logged_in = True
        except Exception:
            self.login_data["cookie"] = None
            self.login_data["message"] = "Login failed"
            self.logged_in = False

        return self.logged_in

    def get_login_data(self):
        return self.login_data
