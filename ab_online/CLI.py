import argparse
import sys

from .API import API

class CLI:

    def __init__(self, args):
        
        self.api = API()

        self.parser = argparse.ArgumentParser(prog="ab-online",description="Launch reproducible Activity Browser sessions and distribute them using NoVNC.")
        subparsers = self.parser.add_subparsers(title="commands")
        self.parser.set_defaults(func=self.parser.print_help)
        
        start = subparsers.add_parser("start",
                                      description="Start a session.",
                                      help="start a session")
        start.set_defaults(func=self.api.start)
        start.add_argument("-f","--force", action="store_true",
                           help="restart if already started")
        start.add_argument("-a","--all", action="store_true",
                           help="start all sessions")
        start.add_argument("-b","--build", action="store_true",
                           help="force rebuilding docker image")
        start.add_argument("-r","--reset", action="store_true",
                           help="delete session containers storage")
        start.add_argument("session", nargs="?", default="", 
                           help="session name")

        build = subparsers.add_parser("build",
                                      description="Build a session.",
                                      help="build a session")
        build.set_defaults(func=self.api.build)
        build.add_argument("-a","--all", action="store_true",
                           help="build all sessions")
        build.add_argument("session", nargs="?", default="", 
                           help="session name")

        stop = subparsers.add_parser("stop",
                                     description="Stop a running session.",
                                     help="stop a running session")
        stop.set_defaults(func=self.api.stop)
        stop.add_argument("-a","--all", action="store_true",
                          help="stop all sessions")
        stop.add_argument("-r","--reset", action="store_true",
                          help="delete session containers storage")
        stop.add_argument("session", nargs="?", default="", 
                          help="session name")
        
        ps = subparsers.add_parser("list",aliases=['ps'], 
                                   description="List sessions.",
                                   help="list sessions")
        ps.set_defaults(func=self.api.ps)
        ps.add_argument("-r","--running", action="store_true",
                            help="print only running sessions")

        self.run(args)

    def run(self, args):
        args = self.parser.parse_args(args)
        func = args.__dict__.pop('func')
        func(**vars(args))






