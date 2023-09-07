import sys

from .client import Client
from .controllers import Docker, Machine, Sessions, Storage
from .session import Database, Plugin, Project, Session
from .api import API


def run_ab_online():
    Storage.init_storage()
    Sessions.read_sessions()
    client = Client()
    client.run(sys.argv[1:])
