from ..controllers import *


class session:
    def __init__(self):
        pass

    # Start/Stop

    @staticmethod
    def start(sessions: list[str], all=False, force=False, build=True, reset=False):
        """start session(s)

        :param sessions: a list of sessions names
        :type sessions: list[str]
        :param all: start all sessions, defaults to False
        :type all: bool, optional
        :param force: restart if already started, defaults to False
        :type force: bool, optional
        :param build: build docker image, defaults to True
        :type build: bool, optional
        :param reset: delete existing data before starting, defaults to False
        :type reset: bool, optional
        :raises TypeError: no session provided
        """
        if sessions is None and not all:
            raise TypeError("at least one session name must be provided")
        if all:
            [
                Sessions.start_session(s, force, build, reset)
                for s in Sessions.sessions.values()
            ]
        else:
            [Sessions.start_session(s, force, build, reset) for s in sessions]

    @staticmethod
    def stop(sessions: list[str], all=False, reset=False):
        """stop session(s) if running

        :param sessions: a list of sessions names
        :type sessions: list[str]
        :param all: stop all running sessions, defaults to False
        :type all: bool, optional
        :param reset: delete sessions data, defaults to False
        :type reset: bool, optional
        :raises TypeError: no session provided
        """
        if sessions is None and not all:
            raise TypeError("at least one session name must be provided")
        if all:
            [Sessions.stop_session(s, reset) for s in Sessions.sessions.values()]
        else:
            [Sessions.stop_session(s, reset) for s in sessions]

    # Divers

    @staticmethod
    def build(sessions: list[str], all=False):
        """build session(s) docker image

        :param sessions: a list of sessions names
        :type sessions: list[str]
        :param all: build all sessions, defaults to False
        :type all: bool, optional
        """
        if all:
            [Sessions.build_session(s) for s in Sessions.sessions.values()]
        else:
            [Sessions.build_session(s) for s in sessions]

    @staticmethod
    def reset(sessions: list[str], all=False):
        """delete sessions data

        :param sessions: a list of sessions names
        :type sessions: list[str]
        :param all: reset all sessions, defaults to False
        :type all: bool, optional
        """
        pass

    @staticmethod
    def delete(session: str, reset=True, force=False):
        """delete given session

        :param session: session name
        :type session: str
        :param reset: delete session data, defaults to True
        :type reset: bool, optional
        :param force: delete even if running, defaults to False
        :type force: bool, optional
        """
        pass

    @staticmethod
    def export_json(session: str, stdout=False, file=None):
        """export session to json

        :param session: name of the session to export
        :type session: str
        :param stdout: print json to stdout, defaults to False
        :type stdout: bool, optional
        :param file: file to save json into, defaults to None
        :type file: _type_, optional
        """
        pass

    @staticmethod
    def import_json(session: str, stdin=False, file=None, force=False):
        """import session from json

        :param session: name of the session
        :type session: str
        :param stdin: get data from stdin instead of file, defaults to False
        :type stdin: bool, optional
        :param file: file from which to get data, defaults to None
        :type file: _type_, optional
        :param force: if session already exist replace it, defaults to False
        :type force: bool, optional
        """
        pass

    # Create/Delete/Edit

    @staticmethod
    def create(
        name: str,
        password: str = "",
        machines: int = 1,
        ab_channel: str = "conda-forge",
        ab_version: str = "latest",
        force: bool = False,
    ):
        pass

    class db:
        def __init__(self):
            pass

        @staticmethod
        def add(
            name: str,
        ):
            """add new database to session

            :param name: database name
            :type name: str
            """
            pass
            """List session databases
            """
            pass

        @staticmethod
        def remove(name: str):
            """Remove session database

            :param name: database name
            :type name: str
            """
            pass

    class plugin:
        def __init__(self):
            pass

        @staticmethod
        def add(name: str, channel: str = "conda-forge", version: str = "latest"):
            pass
            """List session plugins
            """
            pass

        @staticmethod
        def remove(name: str):
            """Remove session plugin

            :param name: database name
            :type name: str
            """
            pass

    class project:
        def __init__(self):
            pass

        @staticmethod
        def add(name: str, databases: list[str], plugins: list[str]):
            pass

        @staticmethod
        def remove(name: str):
            """Remove session project

            :param name: database name
            :type name: str
            """
            pass
