import os

from .controllers.docker import DockerController
from .controllers.data import DataController

class API:

    def __init__(self):
        self.docker_ctrl = DockerController()
        self.data_ctrl = DataController()

    def start_session(self, sessions, all=False, force=False, build=True, reset=False):
        """start given session
        """
        if sessions is None:
            raise TypeError("at least one session name must be provided")
        if all:
            [self.docker_ctrl.start_session(s,force,build,reset) for s in self.docker_ctrl.sessions.values()]
        else:
            [self.docker_ctrl.start_session(s,force,build,reset) for s in sessions]

    def stop_session(self, session, all=False, reset=False):
        """stop given session
        """
        if all:
            [self.docker_ctrl.stop_session(s,reset) for s in self.docker_ctrl.sessions.values()]
        else:
            self.docker_ctrl.stop_session(session, reset)

    def build_session(self, session, all=False):
        """build given session
        """
        if all:
            [self.docker_ctrl.build_session(s) for s in self.docker_ctrl.sessions.values()]
        else:
            self.docker_ctrl.build_session(session)       
    
    def list_sessions(self, running=False):
        """list existing sessions
        """
        return [s.esc_name for s in self.docker_ctrl.sessions.values()]

    def validate_file(self, file):
        """perform checks on a session file
        """
        return "Not yet implemented"
