import os

from .controller import Controller

class API:

    def __init__(self):
        self.ctrl = Controller()

    def start(self, session, all=False, force=False, build=True, reset=False):
        """start given session
        """
        print(session)
        if all:
            [self.ctrl.start_session(s,force,build,reset) for s in self.ctrl.sessions.values()]
        else:
            self.ctrl.start_session(session,force,build,reset)

    def stop(self, session, all=False, reset=False):
        """stop given session
        """
        if all:
            [self.ctrl.stop_session(s,reset) for s in self.ctrl.sessions.values()]
        else:
            self.ctrl.stop_session(session, reset)

    def build(self, session, all=False):
        """build given session
        """
        if all:
            [self.ctrl.build_session(s) for s in self.ctrl.sessions.values()]
        else:
            self.ctrl.build_session(session)       
    
    def ps(self, running=False):
        """list existing sessions
        """
        [print(s.esc_name) for s in self.ctrl.sessions.values()]