"""Flask extension for rapid GitHub app development"""

import hmac
import logging

from flask import abort, current_app, jsonify, make_response, request
from github3 import GitHub, GitHubEnterprise
from werkzeug.exceptions import BadRequest

LOG = logging.getLogger(__name__)

STATUS_FUNC_CALLED = "HIT"
STATUS_NO_FUNC_CALLED = "MISS"


class GitHubAppError(Exception):
    pass


class GitHubAppValidationError(GitHubAppError):
    pass


class GitHubApp(object):
    """The GitHubApp object provides the central interface for interacting GitHub hooks
    and creating GitHub app clients.

    GitHubApp object allows using the "on" decorator to make GitHub hooks to functions
    and provides authenticated github3.py clients for interacting with the GitHub API.

    Keyword Arguments:
        app {Flask object} -- App instance - created with Flask(__name__) (default: {None})
    """

    def __init__(self, app=None):
        self._hook_mappings = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initializes GitHubApp app by setting configuration variables.

        The GitHubApp instance is given the following configuration variables by calling on Flask's configuration:

        `GITHUBAPP_ID`:

            GitHub app ID as an int (required).
            Default: None

        `GITHUBAPP_KEY`:

            Private key used to sign access token requests as bytes or utf-8 encoded string (required).
            Default: None

        `GITHUBAPP_SECRET`:

            Secret used to secure webhooks as bytes or utf-8 encoded string (required). set to `False` to disable
            verification (not recommended for production).
            Default: None

        `GITHUBAPP_URL`:

            URL of GitHub API (used for GitHub Enterprise) as a string.
            Default: None

        `GITHUBAPP_ROUTE`:

            Path used for GitHub hook requests as a string.
            Default: '/'
        """
        required_settings = ["GITHUBAPP_ID", "GITHUBAPP_KEY", "GITHUBAPP_SECRET"]
        for setting in required_settings:
            if not setting in app.config:
                raise RuntimeError(
                    "Flask-GitHubApp requires the '%s' config var to be set" % setting
                )

        app.add_url_rule(
            app.config.get("GITHUBAPP_ROUTE", "/"),
            view_func=self._flask_view_func,
            methods=["POST"],
        )

    @property
    def id(self):
        return current_app.config["GITHUBAPP_ID"]

    @property
    def key(self):
        key = current_app.config["GITHUBAPP_KEY"]
        if hasattr(key, "encode"):
            key = key.encode("utf-8")
        return key

    @property
    def secret(self):
        secret = current_app.config["GITHUBAPP_SECRET"]
        if hasattr(secret, "encode"):
            secret = secret.encode("utf-8")
        return secret

    @property
    def _api_url(self):
        return current_app.config["GITHUBAPP_URL"]

    @property
    def client(self):
        """Unauthenticated GitHub client"""
        if current_app.config.get("GITHUBAPP_URL"):
            return GitHubEnterprise(current_app.config["GITHUBAPP_URL"])
        return GitHub()

    @property
    def payload(self):
        """GitHub hook payload"""
        if request and request.json and "installation" in request.json:
            return request.json

        raise RuntimeError(
            "Payload is only available in the context of a GitHub hook request"
        )

    @property
    def installation_client(self):
        """GitHub client authenticated as GitHub app installation"""
        # Get the current application context
        ctx = current_app.app_context()
        if ctx is not None:
            if not hasattr(ctx, "githubapp_installation"):
                client = self.client
                client.login_as_app_installation(
                    self.key, self.id, self.payload["installation"]["id"]
                )
                ctx.githubapp_installation = client
            return ctx.githubapp_installation

    @property
    def app_client(self):
        """GitHub client authenticated as GitHub app"""
        ctx = current_app.app_context()
        if ctx is not None:
            if not hasattr(ctx, "githubapp_app"):
                client = self.client
                client.login_as_app(self.key, self.id)
                ctx.githubapp_app = client
            return ctx.githubapp_app

    @property
    def installation_token(self):
        return self.installation_client.session.auth.token

    def on(self, event_action):
        """Decorator routes a GitHub hook to the wrapped function.

        Functions decorated as a hook recipient are registered as the function for the given GitHub event.

        @github_app.on('issues.opened')
        def cruel_closer():
            owner = github_app.payload['repository']['owner']['login']
            repo = github_app.payload['repository']['name']
            num = github_app.payload['issue']['id']
            issue = github_app.installation_client.issue(owner, repo, num)
            issue.create_comment('Could not replicate.')
            issue.close()

        Arguments:
            event_action {str} -- Name of the event and optional action (separated by a period), e.g. 'issues.opened' or
                'pull_request'
        """

        def decorator(f):
            if event_action not in self._hook_mappings:
                self._hook_mappings[event_action] = [f]
            else:
                self._hook_mappings[event_action].append(f)

            # make sure the function can still be called normally (e.g. if a user wants to pass in their
            # own Context for whatever reason).
            return f

        return decorator

    def _validate_request(self):
        if not request.is_json:
            raise GitHubAppValidationError(
                "Invalid HTTP Content-Type header for JSON body "
                "(must be application/json or application/*+json)."
            )

        try:
            request.json
        except BadRequest:
            raise GitHubAppValidationError("Invalid HTTP body (must be JSON).")

        event = request.headers.get("X-GitHub-Event")

        if event is None:
            raise GitHubAppValidationError("Missing X-GitHub-Event HTTP header.")

        action = request.json.get("action")

        return event, action

    def _flask_view_func(self):
        functions_to_call = []
        calls = {}

        try:
            event, action = self._validate_request()
        except GitHubAppValidationError as e:
            LOG.error(e)
            error_response = make_response(
                jsonify(status="ERROR", description=str(e)), 400
            )
            return abort(error_response)

        if current_app.config["GITHUBAPP_SECRET"] is not False:
            self._verify_webhook()

        if event in self._hook_mappings:
            functions_to_call += self._hook_mappings[event]

        if action:
            event_action = ".".join([event, action])
            if event_action in self._hook_mappings:
                functions_to_call += self._hook_mappings[event_action]

        if functions_to_call:
            for function in functions_to_call:
                calls[function.__name__] = function()
            status = STATUS_FUNC_CALLED
        else:
            status = STATUS_NO_FUNC_CALLED
        return jsonify({"status": status, "calls": calls})

    def _verify_webhook(self):
        signature_header = "X-Hub-Signature-256"
        signature_header_legacy = "X-Hub-Signature"

        if request.headers.get(signature_header):
            signature = request.headers[signature_header].split("=")[1]
            digestmod = "sha256"
        elif request.headers.get(signature_header_legacy):
            signature = request.headers[signature_header_legacy].split("=")[1]
            digestmod = "sha1"
        else:
            LOG.warning(
                "Signature header missing. Configure your GitHub App with a secret or set GITHUBAPP_SECRET"
                "to False to disable verification."
            )
            return abort(400)

        mac = hmac.new(self.secret, msg=request.data, digestmod=digestmod)

        if not hmac.compare_digest(mac.hexdigest(), signature):
            LOG.warning("GitHub hook signature verification failed.")
            return abort(400)
