from flask import jsonify, request

from ..controllers import Sessions, Storage
from .. import config as CONFIG


class session:
    # Start/Stop

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
        sessions = [s for s in Sessions.sessions.keys()]
        if CONFIG.SERVER_MODE:
            return jsonify(sessions)
        else:
            return sessions

    @staticmethod
    def start(session: str, all=False, force=False, build=True, reset=False):
        """start session(s)

        :param sessions: a list of sessions names
        :type sessions: str
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
        if CONFIG.SERVER_MODE:
            all = request.args.get("all", default=False, type=bool)
            force = request.args.get("force", default=False, type=bool)
            build = request.args.get("build", default=True, type=bool)
            reset = request.args.get("reset", default=False, type=bool)
        if session is None and not all:
            raise TypeError("at least one session name must be provided")
        if all:
            for session in Sessions.sessions.values():
                Sessions.start_session(session, force, build, reset)
        else:
            Sessions.start_session(session, force, build, reset)
        if CONFIG.SERVER_MODE:
            return jsonify("OK")

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
            for session in Sessions.sessions.values():
                Sessions.stop_session(session, reset)
        else:
            for session in sessions:
                Sessions.stop_session(session, reset)

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
            for session in Sessions.sessions.values():
                Sessions.build_session(session)
        else:
            for session in sessions:
                Sessions.build_session(session)

    @staticmethod
    def reset(sessions: list[str], all=False):
        """delete sessions data

        :param sessions: a list of sessions names
        :type sessions: list[str]
        :param all: reset all sessions, defaults to False
        :type all: bool, optional
        """
        if all:
            for session in Sessions.sessions.values():
                Storage.delete_folder(f"sessions_storage/{session}")
        else:
            for session in sessions:
                Storage.delete_folder(f"sessions_storage/{session}")

    @staticmethod
    def delete(session_name: str, reset=True, force=False):
        """delete given session

        :param session_name: session name
        :type session_name: str
        :param reset: delete session data, defaults to True
        :type reset: bool, optional
        :param force: delete even if running, defaults to False
        :type force: bool, optional
        """
        session = Sessions.sessions[session_name]
        if Sessions.is_running(session):
            Sessions.stop_session(session, reset_storage=True)
        Storage.delete_file(f"sessions/{session.esc_name}")
        Sessions.delete_storage(session)

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
    def import_json(name: str, stdin=False, file=None, force=False):
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
        if file:
            esc_name = name.replace(" ", "_").lower()
            Storage.add_file(file,f"{esc_name}.json","sessions",force)
        elif stdin:
            print("import from stdin is not yet supported")
        else:
            print("Error: file or stdin must be provided")