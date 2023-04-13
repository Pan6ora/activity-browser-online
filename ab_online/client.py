import os

from .controller import Controller

class Client:

    def __init__(self):
        self.ctrl = Controller()

    def exit(self):
        quit()

    def help(self):
        os.system("cat manual")

    def clear(self):
        os.system("clear")

    def start(self, session_name, force_build=True, reset_storage=False):
        """start given session
        """
        self.ctrl.start_session(session_name, force_build)

    def stop(self, session_name, reset_storage=False):
        """stop given session
        """
        self.ctrl.stop_session(session_name, reset_storage)
    
    def ps(self, running=False):
        """list existing sessions
        """
        for session in self.ctrl.sessions.values():
            print(session.esc_name)

    def run(self, cmd):
        if isinstance(cmd, str):
            cmd = [cmd,]
        if cmd[0] == "machine":
            pass
        else:
            cmd[0] = "ps" if cmd[0] == "list" else cmd[0]
            args = "" if len(cmd) == 1 else '"'+'","'.join(cmd[1:])+'"'
            cmd = f"self.{cmd[0]}({args})"
            exec(cmd)
