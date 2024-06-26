import json
import bcrypt
import sys
from .. import config as CONFIG
from .plugin import Plugin
from .database import Database
from .project import Project


class Session:
    """AB Online session"""

    def __init__(self, file=None, session_dict=None):
        """instantiate a session from a
        json file"""
        self.dict: dict
        self.file: str  #: path of json file of the session
        self.name: str  #: session name
        self.esc_name: str  #: escaped name (without spaces)
        self.tag: str  #: docker session image tag
        self.password: str  #: session connection password
        self.machines: int  #: number of machines
        self.ab_channel: str  #: Activity Browser anaconda channel
        self.ab_version: str  #: Activity Browser conda version
        self.plugins: dict[str, Plugin] = {}  #: session plugins
        self.databases: dict[str, Database] = {}  #: session databases
        self.projects: dict[str, Project] = {}  #: session projects

        if file:
            self.populate(file=file)
        elif session_dict:
            self.populate(session_dict=session_dict)

    def hash_password(self):
        bytes = self.password.encode("utf-8")
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(bytes, salt)
        return hash

    def populate(self, session_dict=None, file=None):
        """Populate session values from a session file"""
        if file:
            session_dict = self.from_json(file)
        self.dict = self.validate_session(session_dict)
        if isinstance(self.dict, str):
            print("Error:"+self.dict)
            exit(1)
        # Populate session infos
        self.file = file
        self.name = self.dict["name"]
        self.esc_name = self.name.replace(" ", "_").lower()
        self.tag = f"ab_online/session:{self.esc_name}"
        self.password = self.dict["password"]
        self.machines = int(self.dict["machines"])
        self.ab_channel = self.dict["ab_channel"]
        self.ab_version = self.dict["ab_version"]
        if not file:
            self.file = f"{CONFIG.STORAGE}/sessions/{self.esc_name}.json"
        else:
            self.file = file
        # Populate plugins list
        for x in self.dict["plugins"]:
            self.plugins[x["name"]] = Plugin(
                x["name"], x["ab_channel"], x["version"])
        # Populate databases list
        for x in self.dict["databases"]:
            self.databases[x["name"]] = Database(
                x["name"], x["filename"], x["location"]
            )
        # Populate projects list
        for x in self.dict["projects"]:
            project = Project(x["name"])
            for db in x["databases"]:
                project.add_database(self.databases[db])
            for plugin in x["plugins"]:
                project.add_plugin(self.plugins[plugin])
            self.projects[x["name"]] = project

    def from_json(self, file: str):
        """Convert json file to python dict

        :return: a new dictionary with json content
        :rtype: dict
        """
        with open(file) as f:
            result_dict = json.load(f)
            return result_dict

    def to_json(self):
        json_object = json.dumps(self.dict, indent=4)
        return json_object

    def validate_session(self, session_dict):
        """perform a list of tests on a
        session to check if it is valid
        """
        # check primary key list
        for key in [
            "name",
            "password",
            "machines",
            "ab_channel",
            "ab_version",
            "databases",
            "plugins",
            "projects",
        ]:
            if key not in session_dict:
                return f"'{key}' entry missing"
        # check databases keys
        for database in session_dict["databases"]:
            for key in ["name", "location", "filename"]:
                if key not in database:
                    return f"a database has no {key}"
        # check plugins keys
        for plugin in session_dict["plugins"]:
            for key in ["name", "ab_channel", "version"]:
                if key not in plugin:
                    return f"a plugin has no {key}"
        # check projects keys
        for project in session_dict["projects"]:
            for key in ["name", "databases", "plugins"]:
                if key not in project:
                    return f"a project has no {key}"

        databases = [
            "databases",
            [x["name"] for x in session_dict["databases"]],
        ]
        plugins = [
            "plugins",
            [x["name"] for x in session_dict["plugins"]],
        ]
        projects = [
            "projects",
            [x["name"] for x in session_dict["projects"]],
        ]
        # check entries with same name
        for entries in [databases, plugins, projects]:
            if len(entries[1]) != len(list(set(entries[1]))):
                return f"2 or more {entries[0]} with same name exist"
        # check for non-existing entries
        for project in session_dict["projects"]:
            for db in project["databases"]:
                if db not in databases[1]:
                    return f"{db} database in project '{project['name']}' not in main databases list"
            for pl in project["plugins"]:
                if pl not in plugins[1]:
                    return f"{pl} plugin in project '{project['name']}' not in main plugins list"
        return session_dict
