from ..controllers import *


class API:
    from .session import session
    from .db import db

    def __init__(self):
        pass

    def validate_file(self, file):
        """perform checks on a session file"""
        pass

    @staticmethod
    def list_sessions(config=False, storage=False, state=False, running=False):
        """list existing sessions

        :param config: show sessions configuration, defaults to False
        :type config: bool, optional
        :param storage: show sessions data infos, defaults to False
        :type storage: bool, optional
        :param state: show running state, defaults to False
        :type state: bool, optional
        :param running: show only running sessions, defaults to False
        :type running: bool, optional
        """
        return [s.esc_name for s in Sessions.sessions.values()]

    @staticmethod
    def list_databases(verbose=False):
        """list existing databases

        :param verbose: show infos about database, defaults to False
        :type verbose: bool, optional
        """
        return Storage.list_files("databases", extension=False)
