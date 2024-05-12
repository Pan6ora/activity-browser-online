from flask import jsonify, request

from ..controllers import Sessions, Storage
from ..session import Session
from .. import config as CONFIG


class session:
    # Start/Stop

    @staticmethod
    def list(config=False, storage=False, state=False, running=False):
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
        if CONFIG.SERVER_MODE:
            config = request.args.get("config", default=False, type=bool)
            storage = request.args.get("storage", default=False, type=bool)
            state = request.args.get("state", default=False, type=bool)
            running = request.args.get("running", default=False, type=bool)
        if running:
            sessions = [
                s.esc_name for s in Sessions.sessions.values() if Sessions.is_running(s)
            ]
        else:
            sessions = [s.esc_name for s in Sessions.sessions.values()]
        if CONFIG.SERVER_MODE:
            return jsonify(sessions)
        else:
            return sessions

    @staticmethod
    def start(session: str, all=False, force=False, build=True, reset=False):
        """start session

        :param session: session
        :type session: str
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
    def stop(session: str, all=False, reset=False):
        """stop session if running

        :param session: session
        :type session: str
        :param all: stop all running sessions, defaults to False
        :type all: bool, optional
        :param reset: delete session data, defaults to False
        :type reset: bool, optional
        :raises TypeError: no session provided
        """
        if CONFIG.SERVER_MODE:
            all = request.args.get("all", default=False, type=bool)
            reset = request.args.get("reset", default=False, type=bool)
        if session is None and not all:
            raise TypeError("at least one session name must be provided")
        if all:
            for session in Sessions.sessions.values():
                Sessions.stop_session(session, reset)
        else:
            Sessions.stop_session(session, reset)

    # Divers

    @staticmethod
    def build(session: str, all=False):
        """build session docker image

        :param session: session
        :type session: str
        :param all: build all sessions, defaults to False
        :type all: bool, optional
        """
        if CONFIG.SERVER_MODE:
            all = request.args.get("all", default=False, type=bool)
        if all:
            for session in Sessions.sessions.values():
                Sessions.build_session(session)
        else:
            Sessions.build_session(session)

    @staticmethod
    def reset(session: str, all=False):
        """delete sessions data

        :param session: session
        :type session: str
        :param all: reset all sessions, defaults to False
        :type all: bool, optional
        """
        if CONFIG.SERVER_MODE:
            all = request.args.get("all", default=False, type=bool)
        if all:
            for session in Sessions.sessions.values():
                Storage.delete_folder(f"sessions_storage/{session}")
        else:
            Storage.delete_folder(f"sessions_storage/{session}")

    @staticmethod
    def delete(session: str, reset=True, force=False):
        """delete given session

        :param session: session
        :type session: str
        :param reset: delete session data, defaults to True
        :type reset: bool, optional
        :param force: delete even if running, defaults to False
        :type force: bool, optional
        """
        if CONFIG.SERVER_MODE:
            reset = request.args.get("reset", default=False, type=bool)
            force = request.args.get("force", default=False, type=bool)
        session_obj = Sessions.sessions[session]
        if Sessions.is_running(session_obj):
            Sessions.stop_session(session_obj, reset_storage=True)
        Storage.delete_file(f"sessions/{session.esc_name}")
        Sessions.delete_storage(session_obj)

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
        if isinstance(session, str):
            if session not in Sessions.sessions.keys():
                raise ValueError(f"session '{session}' does not exist")
            else:
                session = Sessions.sessions[session]
        json_object = session.to_json()
        if stdout:
            print(json_object)
        if file:
            with open(file, "w") as outfile:
                outfile.write(json_object)
        return json_object

    @staticmethod
    def import_json(name: str, file, force=False):
        """import session from json

        :param session: name of the session
        :type session: str
        :param file: file from which to get data
        :type file: str
        :param force: if session already exist replace it, defaults to False
        :type force: bool, optional
        """
        if file:
            esc_name = name.replace(" ", "_").lower()
            Storage.add_file(file, f"{esc_name}.json", "sessions", force)
        else:
            print("Error: file must be provided")

    @staticmethod
    def import_dict(session_dict):
        session = Session(session_dict=session_dict)
        Sessions.add_session(session)
        
        return session
