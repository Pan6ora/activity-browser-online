import argparse
import sys

from .api import API
from . import config
from .controllers import Machine


class Parser(argparse.ArgumentParser):
    """Modified argparse ArgumentParser"""

    def error(self, message):
        sys.stderr.write("\nerror: %s\n\n" % message)
        self.print_help()
        sys.stderr.write("\n")
        sys.exit(2)

    def print_help(self, **kwargs):
        """Allow original print_help() to take arguments"""
        argparse.ArgumentParser.print_help(self)


class Client:
    def __init__(self):
        self.api = API()
        self.parser = self.generate_parser()

    def generate_parser(self):
        parser = Parser(
            prog="ab-online",
            description="Launch reproducible Activity Browser sessions and distribute them using NoVNC.",
        )
        subparsers = parser.add_subparsers(title="commands")
        parser.set_defaults(func=parser.print_help)

        parser.add_argument(
            "--debug", action="store_true", help="display debug informations"
        )
        parser.add_argument("--storage", nargs="?", help="path of storage folder")
        parser.add_argument(
            "--dev", action="store_true", help="use local code instead of conda package"
        )

        start = subparsers.add_parser(
            "start", description="Start session(s).", help="start session(s)"
        )
        start.set_defaults(func=self.api.session.start)
        start.add_argument(
            "-f", "--force", action="store_true", help="restart if already started"
        )
        start.add_argument(
            "-a", "--all", action="store_true", help="start all sessions"
        )
        start.add_argument(
            "-b", "--build", action="store_true", help="force rebuilding docker image"
        )
        start.add_argument(
            "-r",
            "--reset",
            action="store_true",
            help="delete session containers storage",
        )
        start.add_argument("sessions", nargs="*", help="session(s) name(s)")

        build = subparsers.add_parser(
            "build", description="Build session(s).", help="build session(s)"
        )
        build.set_defaults(func=self.api.session.build)
        build.add_argument(
            "-a", "--all", action="store_true", help="build all sessions"
        )
        build.add_argument("sessions", nargs="*", default="", help="session(s) names")

        stop = subparsers.add_parser(
            "stop",
            description="Stop running session(s).",
            help="stop running session(s)",
        )
        stop.set_defaults(func=self.api.session.stop)
        stop.add_argument("-a", "--all", action="store_true", help="stop all sessions")
        stop.add_argument(
            "-r",
            "--reset",
            action="store_true",
            help="delete session containers storage",
        )
        stop.add_argument("sessions", nargs="*", default="", help="session(s) name")

        ps = subparsers.add_parser(
            "list", aliases=["ps"], description="List sessions.", help="list sessions"
        )
        ps.set_defaults(func=self.api.session.list_sessions)
        ps.add_argument(
            "-r", "--running", action="store_true", help="print only running sessions"
        )

        server = subparsers.add_parser(
            "server", description="Start http API server", help="start http API server"
        )
        server.set_defaults(func=self.api.run_server)
        setup = subparsers.add_parser(
            "setup",
            description="Setup AB inside a machine",
            help="setup AB inside a machine",
        )
        setup.set_defaults(func=Machine.setup_session)
        setup.add_argument("session_file", nargs="+", default="", help="a session file")
        return parser

    def run(self, args, debug=True):
        args = self.parser.parse_args(args)
        func = args.__dict__.pop("func")

        # manage global settings
        config.DEBUG = args.__dict__.pop("debug")
        storage = args.__dict__.pop("storage")
        dev = args.__dict__.pop("dev")
        if storage:
            config.STORAGE = True
        if dev:
            config.DEV = True

        # execute command
        if config.DEBUG:
            print("Debug mode")
            print(f"Storage path: {config.STORAGE}\n")
            result = func(**vars(args))
            self.pretty_print(result)
        else:
            try:
                result = func(**vars(args))
                self.pretty_print(result)
            except Exception as e:
                print(f"error: {e}")

    def pretty_print(self, value):
        """print object depending it's type"""
        if isinstance(value, str):
            print(value)
        elif isinstance(value, int):
            print(value)
        elif isinstance(value, list):
            [self.pretty_print(i) for i in value]


def get_parser():
    """This function is only used to generated the client
    documentation with Sphinx
    """
    client = Client()
    return client.generate_parser()
