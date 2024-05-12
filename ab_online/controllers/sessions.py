import json
from string import Template

from .. import config as CONFIG
from .storage import Storage
from .docker import Docker
from ..session import Session


class Sessions:
    storage_path = f"{CONFIG.STORAGE}/sessions_storage"
    running_sessions: list[Session] = []
    sessions = {}

    @classmethod
    def read_sessions(cls):
        """load all session files and return them
        as a dictionary of Session objects
        """
        sessions = {}
        for file in Storage.list_files("sessions"):
            session = Session(f"{CONFIG.STORAGE}/sessions/{file}")
            sessions[session.esc_name] = session
            cls.create_storage(session)
        cls.sessions = sessions
        return sessions

    @classmethod
    def add_session(cls, session: Session):
        cls.sessions[session.esc_name] = session

    @classmethod
    def remove_session(cls, session: Session):
        cls.sessions.pop(session.esc_name)

    @classmethod
    def save_session(cls, session):
        if isinstance(session, str):
            if session not in cls.sessions.keys():
                raise ValueError(f"session '{session}' does not exist")
            else:
                session = cls.sessions[session]

    @classmethod
    def is_running(cls, session):
        networks = Docker.client.networks.list(names=session.esc_name)
        return bool(networks)

    @classmethod
    def set_running_sessions(cls):
        cls.running_sessions = [
            s for s in cls.sessions.values() if cls.is_running(s)]
        if not cls.running_sessions:
            cls.stop_proxy()
        cls.generate_main_home()
        cls.generate_caddyfile()
        cls.generate_users_file()

    @classmethod
    def build_session(cls, session):
        if isinstance(session, str):
            if session not in cls.sessions.keys():
                raise ValueError(f"session '{session}' does not exist")
            else:
                session = cls.sessions[session]
        Docker.build_session(session)

    @classmethod
    def start_session(
        cls, session, restart=False, force_build=False, reset_storage=False
    ):
        """start all machines from the given session

        session: a Session object or the name of a session file from data/sessions
        force_build: wether to build session container if already exist
        reset_storage: wether to delete past runs session storage
        """

        if isinstance(session, str):
            if session not in cls.sessions.keys():
                raise ValueError(f"session '{session}' does not exist")
            else:
                session = cls.sessions[session]

        print(f"Starting '{session.name}' session...")

        print("  - stop existing session")
        cls.stop_session(session, reset_storage)

        print(f"  - create '{session.esc_name}' network")
        Docker.client.networks.create(session.esc_name)

        tag = "ab_online/novnc:latest"
        try:
            Docker.client.images.get(tag)
        except:
            print("  - build novnc image")
            Docker.build_novnc()

        tag = f"ab_online/{session.ab_channel}:{session.ab_version.replace('+','')}"
        try:
            Docker.client.images.get(tag)
        except:
            print("  - build Activity Browser image")
            Docker.build_ab(session.ab_channel, session.ab_version)

        try:
            Docker.client.images.get(session.tag)
        except:
            force_build = True
        if force_build:
            print("  - build session image")
            Docker.build_session(session)

        print("  - create storage")
        cls.create_storage(session, reset_storage)

        print("  - create tokens")
        cls.generate_tokens_file(session)

        print("  - create home")
        cls.generate_session_home(session)

        print("  - create main network")
        Docker.create_main_network()

        print("  - start novnc container")
        Docker.start_novnc_gate(session)

        print(
            f"  - start {session.machines} containers from image {session.tag}")
        for id in range(session.machines):
            Docker.start_machine(session, id=id)

        print("  - start proxy container")
        Docker.stop_proxy()
        cls.start_proxy()

        cls.set_running_sessions()
        Docker.reload_caddyfile()
        print("Done !")

    @classmethod
    def stop_proxy(cls):
        print("  - stop proxy")
        Docker.stop_proxy()
        print("  - remove main network")
        Docker.remove_main_network()

    @classmethod
    def start_proxy(cls):
        cls.generate_caddyfile()
        cls.generate_users_file()
        try:
            Docker.start_caddy_proxy()
        except:
            Docker.reload_caddyfile()

    @classmethod
    def stop_session(cls, session, reset_storage=False):
        """Stop given machine if running

        reset_storage: delete session data from the computer
        """

        if isinstance(session, str):
            session = cls.sessions[session]

        print("  - stop existing containers")
        Docker.stop_containers(session)

        print(f"  - remove existing '{session.esc_name}' network")
        Docker.remove_network(session)

        if reset_storage:
            print(f"  - delete session storage")
            cls.delete_storage(session)

        cls.set_running_sessions()

    @classmethod
    def delete_storage(cls, session):
        Storage.delete_folder(f"sessions_storage/{session.esc_name}")

    @classmethod
    def create_storage(cls, session, reset_storage=False):
        if reset_storage:
            cls.delete_storage(session)
        Storage.create_folder(f"sessions_storage/{session.esc_name}")
        Storage.create_folder(f"sessions_storage/{session.esc_name}/databases")
        for db in session.databases.values():
            Storage.add_file(
                f"{CONFIG.STORAGE}/databases/{db.filename}",
                db.filename,
                f"sessions_storage/{session.esc_name}/databases",
                link=True,
            )
        for i in range(session.machines):
            Storage.create_folder(f"sessions_storage/{session.esc_name}/{i}")

    @classmethod
    def generate_tokens_file(cls, session):
        Storage.create_folder(f"sessions_storage/{session.esc_name}/novnc")
        with open(
            f"{cls.storage_path}/{session.esc_name}/novnc/token.list", "w"
        ) as file:
            for i in range(session.machines):
                file.write(f"{i}: {session.esc_name}-{i}:5901\n")

    @classmethod
    def generate_session_home(cls, session):
        Storage.create_folder(f"sessions_storage/{session.esc_name}/home")
        with open(
            f"{cls.storage_path}/{session.esc_name}/home/index.html", "w"
        ) as file:
            for i in range(session.machines):
                file.write(
                    f'<a href="https://{session.esc_name}.{CONFIG.DOMAIN}/vnc.html?autoconnect=true&resize=remote&amp;path=novnc/websockify?token={i}">Machine n°{i}</a><br>\n'
                )
        Storage.add_file(
            f"{CONFIG.INCLUDES}/httpd.conf",
            "httpd.conf",
            f"sessions_storage/{session.esc_name}/home",
        )

    @classmethod
    def generate_main_home(cls):
        Storage.create_folder("proxy/static")
        with open(f"{CONFIG.STORAGE}/proxy/static/index.html", "w") as file:
            for session in cls.running_sessions:
                file.write(
                    f'<a href="https://home.{session.esc_name}.{CONFIG.DOMAIN}">{session.name}</a><br>\n'
                )

    @classmethod
    def generate_users_file(cls):
        users_dict = {"users": []}
        for session in cls.running_sessions:
            id = session.esc_name + "0" * (36 - len(session.esc_name))
            users_dict["users"].append(
                {
                    "id": id,
                    "username": session.esc_name,
                    "passwords": [{"hash": session.hash_password().decode()}],
                    "roles": [{"name": session.esc_name, "organization": "authp"}],
                }
            )
        json_object = json.dumps(users_dict, indent=4)
        with open(f"{CONFIG.STORAGE}/proxy/users.json", "w") as outfile:
            outfile.write(json_object)

    @classmethod
    def generate_caddyfile(cls):
        authorization = ""
        redirect = ""
        for session in cls.running_sessions:
            authorization += f"""
            authorization policy {session.esc_name} \u007b\n
            set auth url https://auth.ab-online.localhost/\n
            allow roles authp/{session.esc_name}\n
            }}\n
            """
            redirect += f"""
            {session.esc_name}.{CONFIG.DOMAIN} \u007b\n
            authorize with {session.esc_name}\n
            reverse_proxy {session.esc_name}-gate:8080\n
            }}\n
            home.{session.esc_name}.{CONFIG.DOMAIN} \u007b\n
            authorize with {session.esc_name}\n
            root * /home/storage/{session.esc_name}/home\n
            file_server browse\n
            }}\n
            """
        d = {
            "authorization": authorization,
            "redirect": redirect,
        }
        with open(f"{CONFIG.INCLUDES}/Caddyfile", "r") as f:
            src = Template(f.read())
            result = src.substitute(d)
        with open(f"{CONFIG.STORAGE}/proxy/Caddyfile", "w") as file:
            file.writelines(result)
