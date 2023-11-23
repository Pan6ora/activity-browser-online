import flask
from flask import request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

from ..controllers import *
from .. import config as CONFIG

Storage.init_storage()
Sessions.read_sessions()


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

    @staticmethod
    def not_implemented():
        return jsonify(["Not yet implemented"])

    app.add_url_rule(
        "/api/v1/session/list", "list session", session.list, methods=["GET"]
    )
    app.add_url_rule(
        "/api/v1/session/start/<session>",
        "start session",
        session.start,
        methods=["GET"],
    )
    app.add_url_rule(
        "/api/v1/session/stop/<session>", "stop session", session.stop, methods=["GET"]
    )
    app.add_url_rule(
        "/api/v1/session/build/<session>",
        "build session",
        session.build,
        methods=["GET"],
    )
    app.add_url_rule(
        "/api/v1/session/reset/<session>",
        "reset session",
        session.reset,
        methods=["GET"],
    )
    app.add_url_rule(
        "/api/v1/session/delete/<session>",
        "delete session",
        session.delete,
        methods=["GET"],
    )
    app.add_url_rule(
        "/api/v1/session/export_json",
        "export session",
        not_implemented,
        methods=["GET"],
    )
    app.add_url_rule(
        "/api/v1/session/import_json",
        "import session",
        not_implemented,
        methods=["GET"],
    )

    app.add_url_rule("/api/v1/db/list", "list db", db.list, methods=["GET"])
    app.add_url_rule("/api/v1/db/add", "add db", not_implemented, methods=["GET"])
    app.add_url_rule(
        "/api/v1/db/remove/<name>", "remove db", db.remove, methods=["GET"]
    )
    app.add_url_rule(
        "/api/v1/db/update/<name>", "update db", not_implemented, methods=["GET"]
    )

    @classmethod
    def run_server(cls):
        CONFIG.SERVER_MODE = True
        Sessions.start_proxy()
        cls.web_api.run()
        Sessions.set_running_sessions()
