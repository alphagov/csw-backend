import os
import re
import datetime
from http import cookies
import jwt
import google_auth_oauthlib.flow
from chalicelib.aws.gds_ssm_client import GdsSsmClient
from chalicelib.database_handle import DatabaseHandle
from chalicelib.models import User, UserSession

class AuthHandler:
    """
    Implements Google OAuth flow
    Implements JWT session tokens
    Implements User and Session models

    Gets google console api credentials, token secret and email domain from
    SSM ParameterStore
    TODO - Decouple params and pass to init method?

    Authentication by decoding JWT or by parsing
    Google OAuth return code query string param
    """

    def __init__(self, app):

        # app lets you use shared log method
        self.app = app
        self.dbh = DatabaseHandle(app)

        self.db = self.dbh.get_handle()
        try:
            self.db.connect()
        except Exception as error:
            self.app.log.error("Failed to connect to database: "+str(error))

        # Set time to expiry for session cookie
        self.cookie_expiration = datetime.timedelta(days=1)

        # Retrieve Google OAuth credentials and token secret
        self.get_params()

        # Initialise parameters for OAuth scopes and
        # JWT encryption
        self.flow = None
        self.token_algorithm = 'HS256'

        self.scopes = [
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/plus.me",
            "https://www.googleapis.com/auth/userinfo.email"
        ]

        # TODO move to param store
        self.email_domain = "digital.cabinet-office.gov.uk"

        # Assume logged in status is false until tested
        self.cookie = None
        self.logged_in = False
        self.login_data = {
            'authenticated': False,
            'is_registered': False
        }

    def get_params(self):
        """
        Retrieve the secrets from SSM.
        """

        if 'CSW_ENV' in os.environ:

            env = os.environ['CSW_ENV']

            params = {
                "client_config": f"/csw/google/api-credentials",
                "token_secret": f"/csw/{env}/auth/token_secret"
            }

            # Get list of SSM parameter names from dict
            param_list = list(params.values())

            ssm = GdsSsmClient(self.app)

            # Get all listed parameters in one API call
            parameters = ssm.get_parameters(param_list, True)

            self.token_secret = ssm.get_parameter_value(parameters, params["token_secret"])

            # Because the google creds are JSON they get escaped in the API response
            # and need to be parsed into a dict for use
            google_config_param = ssm.get_parameter_value(parameters, params["client_config"])
            self.client_config = ssm.parse_escaped_json_parameter(google_config_param)

        else:
            self.app.log.debug("Environment variable CSW_ENV missing")

    def get_auth_flow(self, url):
        """
        Get as instance of the Google OAuth flow object
        If the flow object has already been created it can be re-used

        :param str url: The URL to return the user to after the auth process
        :return google_auth_oauthlib.flow:
        """

        if self.flow is None:

            self.flow = google_auth_oauthlib.flow.Flow.from_client_config(self.client_config, self.scopes)
            self.flow.redirect_uri = url

        return self.flow

    def get_auth_url(self, url):

        auth_flow = self.get_auth_flow(url)

        login_url, _ = auth_flow.authorization_url(
            prompt="select_account",
            hd=self.email_domain
        )

        return login_url

    def get_base_url(self, request):
        """
        Returns the base URL from the current request
        At present /app is appended to the URL
        When we implement CloudFront the /app/ should no longer be necessary

        :param dict request: The request object received by API Gateway
        :return str: The URL to return to after the OAuth redirect
        """

        # Set default header for the case where X-Forwarded-Proto header is missing
        # Assume https
        protocol = 'https'
        if 'X-Forwarded-Proto' in request.headers:
            protocol = request.headers['X-Forwarded-Proto']
        return protocol + "://" + request.headers['Host'] + "/app"

    def get_user_token(self, request):
        """
        Gets the session token cookie value

        :param dict request: The request object received by API Gateway
        :return str: The cookie value
        """

        token = self.get_cookie_value(request, "session")
        return token

    def get_cookie_value(self, req, cookie_name):
        """
        Get cookie value or None if missing

        :param dict req: The http request dict
        :param str cookie_name: The name of the cookie to get
        :return str: Value from http cookie
        """

        value = None

        if "cookie" in req.headers:
            cookie = cookies.SimpleCookie()
            cookie.load(req.headers["cookie"])

            if cookie_name in cookie:
                value = cookie[cookie_name].value

        return value

    def read_jwt(self, user_jwt):
        """
        Decode the token data using the secret from SSM

        :param user_jwt: JWT token string
        :return dict: The decoded user data dict
        """

        user = None

        if (user_jwt is not None):
            try:
                user = jwt.decode(user_jwt.encode(), self.token_secret, algorithms=[self.token_algorithm])

            except Exception as error:
                self.app.log.error("Failed to decode session token: " + str(error))

        return user

    def has_valid_user(self, req):
        """
        Read and decode the session JWT.
        The JWT corresponds to an active UserSession record
        The date_accessed field of this record should be updated
        each time the this method is called.

        :param dict req: The request object
        :return dict: The details of the user encoded in the JWT
        """

        user = None

        if "cookie" in req.headers:

            user_jwt = self.get_user_token(req)

            if user_jwt is not None:
                user = self.read_jwt(user_jwt)

                # Update UserSession accessed date
                try:
                    db_user = User.find_active_by_email(user['email'])
                    UserSession.accessed(db_user)
                except Exception as error:
                    self.app.log.error("Failed to update session: "+str(error))

        return user

    def is_valid_user(self, user):
        """

        :param user:
        :return:
        """

        domain_pattern = "\@" + self.email_domain.replace(".", "\\.") + "$"

        domain_valid = bool(re.search(domain_pattern, user['email']))

        # Check against User table for active user record
        try:
            db_user = User.find_active_by_email(user['email'])
            user_registered = True

            # Create UserSession record
            try:
                session = UserSession.start(db_user)
            except Exception as error:
                session = None
                self.app.log.debug("User not registered: " + str(error))
                self.db.rollback()

        except Exception as error:
            user_registered = False
            self.app.log.debug("User not registered: " + str(error))

        valid = domain_valid & user_registered

        return valid

    def generate_cookie_header_val(self, token):
        """
        Generate a session cookie with the default expiry

        :param str token: The value to store in the session cookie
        :return str:
        """

        expiration = datetime.datetime.now() + self.cookie_expiration

        return self.create_set_cookie_header("session", token, expiration)

    def generate_logout_header_val(self):
        """
        Generate a session cookie that expires immediately to force logout

        :return str:
        """

        expiration = datetime.datetime.now()

        # Update closed date on database UserSession
        try:
            db_user = User.find_active_by_email(self.user['email'])
            UserSession.close(db_user)
        except Exception as error:
            self.app.log.error("Failed to close session: "+str(error))
            self.db.rollback()

        return self.create_set_cookie_header("session", None, expiration)

    def create_set_cookie_header(self, cookie_name, cookie_value, expiration):
        """
        Create the value for a Set-Cookie http header for the session cookie

        :param token:
        :param expiration:
        :return:
        """

        cookie = cookies.SimpleCookie()
        cookie[cookie_name] = cookie_value
        cookie[cookie_name]["expires"] = expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
        cookie[cookie_name]["path"] = "/"

        # Workaround the fact that cookie.output returns a string like: 'Set-Cookie: session=650406237; etc..'
        # but we don't want the 'Set-Cookie: ' part in the actual header.
        raw_cookie_output = cookie.output()

        # Remove the Set-Cookie: prefix. Headers are passed as a dict to the response
        cookie_header = raw_cookie_output.replace("Set-Cookie: ", "")

        return cookie_header

    def get_user_from_code(self, url, code):

        flow = self.get_auth_flow(url)

        self.google_token = flow.fetch_token(code=code)

        self.session = flow.authorized_session()

        self.user = self.session.get('https://www.googleapis.com/userinfo/v2/me').json()

        return self.user

    def get_jwt(self, user):

        user_jwt = jwt.encode(user, self.token_secret, algorithm=self.token_algorithm).decode('utf-8')
        return user_jwt

    def try_login(self, req):

        # By default any request is unauthenticated
        # Requests can be authenticated by an un-expired session cookie
        # Or by a response code QS variable from a Google OAuth request

        self.logged_in = False
        self.login_data = {
            'authenticated': False,
            'is_registered': False
        }

        try:

            # First check for session cookie
            # Returns user details object or None if no session cookie
            self.user = self.has_valid_user(req)

            if self.user is not None:

                self.token = self.get_user_token(req)
                self.logged_in = True
                self.login_data['authenticated'] = True
                self.login_data['is_registered'] = True
                self.login_data.update(self.user)

            else:

                # Then check for OAuth response code in QS
                if "code" in req.query_params:

                    url = self.get_base_url(req)
                    code = req.query_params["code"]

                    self.user = self.get_user_from_code(url, code)

                    # Explicitly set authenticated property
                    self.login_data['authenticated'] = self.user['authenticated']
                    # Copy auth result into login_data
                    self.login_data.update(self.user)

                    # Make sure the email Google OAuthed is on the correct domain
                    # This is a secondary protection as the Cloud Console credentials
                    if self.login_data['authenticated']:

                        # Check that the user has an active account in CSW
                        self.login_data['is_registered'] = self.is_valid_user(self.user)

                    # If both authenticated and registered then log them in.
                    if self.login_data['is_registered']:

                        self.user_jwt = self.get_jwt(self.user)

                        self.cookie = self.generate_cookie_header_val(self.user_jwt)

                        self.token = self.user_jwt

                        self.logged_in = True

            if self.logged_in:

                # self.login_data.update(self.user)
                self.login_data["cookie"] = self.cookie
                self.login_data["token"] = self.token

        except Exception as err:

            self.app.log.debug(str(err))
            self.login_data["cookie"] = None
            self.login_data["message"] = "Login failed"
            self.logged_in = False

        return self.logged_in

    def get_login_data(self):

        self.app.log.debug(str(self.login_data))

        return self.login_data
