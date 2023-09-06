import sys

from .client import Client
from .controllers import *


def run_ab_online():
    Storage.init_storage()
    Sessions.read_sessions()
    client = Client()
    client.run(sys.argv[1:])
