import sys

from .machine import Machine

def run_ab_online():
    print(sys.argv)
    if "setup" in sys.argv:
        Machine.setup_session("session.json")
    else:
        from .client import Client
        from .controllers import Storage
        from .controllers import Sessions
        Storage.init_storage()
        Sessions.read_sessions()
        client = Client()
        client.run(sys.argv[1:])
