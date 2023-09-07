import flask
from flask import request
from werkzeug.middleware.proxy_fix import ProxyFix

from ..controllers import *
from .. import config as CONFIG


class WebAPI:
    def __init__(self):
        self.app = flask.Flask(__name__)
        self.app.config["DEBUG"] = CONFIG.DEBUG
        self.app.wsgi_app = ProxyFix(
            self.app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
        )

        @self.app.route("/", methods=["GET"])
        def home():
            return """<h1>Welcome to Activity Browser Online API</h1>
            <p>See documentation on readthedocs to learn about AB Online and this API</p>"""

    def run(self):
        self.app.run()


class API:
    from .session import session
    from .db import db

    web_api = WebAPI()
    app = web_api.app

    @classmethod
    def run_server(cls):
        CONFIG.SERVER_MODE = True
        Sessions.start_proxy()
        cls.web_api.run()

    app.route("/api/v1/sessions/list", methods=["GET"])(session.list_sessions)
    app.route("/api/v1/databases/list", methods=["GET"])(db.list_databases)
    app.route("/api/v1/sessions/start/<session>", methods=["GET"])(session.start)
