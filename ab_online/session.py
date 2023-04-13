import json
import os

class Session:

    def __init__(self,file):
        """instanciate a session from a
        json file"""
        self.file = file
        self.filename = os.path.basename(file)
        self.session_dict = self.file_to_dict()
        self.validate_session_dict()
        
        self.name       = self.session_dict["name"]
        self.esc_name   = self.name.replace(" ", "_")
        self.tag        = f"ab_online/session:{self.esc_name}"
        self.password   = self.session_dict["password"]
        self.machines   = self.session_dict["machines"] 
        self.ab_channel = self.session_dict["ab_channel"]
        self.ab_version = self.session_dict["ab_version"]
        self.plugins = {}
        for x in self.session_dict["plugins"]:
            self.plugins[x["name"]] = Plugin(x)
        self.projects = {}
        for x in self.session_dict["projects"]:
            self.projects[x["name"]] = Project(x)
        self.databases = {}
        for x in self.session_dict["databases"]:
            self.databases[x["name"]] = Database(x)

    def file_to_dict(self):
        f = open(self.file)
        session_dict = json.load(f)
        f.close()
        return session_dict

    def validate_session_dict(self):
        """ perform a list of tests on a
        session to check if it is valid
        """
        # check primary key list
        for key in ["name", 
                    "password", 
                    "machines", 
                    "ab_channel", 
                    "ab_version",
                    "databases",
                    "plugins",
                    "projects" ]:
            if key not in self.session_dict:
                return f"'{key}' entry missing"
        # check databases keys
        for database in self.session_dict["databases"]:
            for key in ["name","location","filename"]:
                if key not in database:
                    return f"a database has no {key}"
        # check plugins keys
        for plugin in self.session_dict["plugins"]:
            for key in ["name","ab_channel","version"]:
                if key not in plugin:
                    return f"a plugin has no {key}"
        # check projects keys
        for project in self.session_dict["projects"]:
            for key in ["name","databases","plugins"]:
                if key not in project:
                    return f"a project has no {key}"

        databases = ["databases",[x["name"] for x in self.session_dict["databases"]],]
        plugins   = ["plugins",[x["name"] for x in self.session_dict["plugins"]],]
        projects  = ["projects",[x["name"] for x in self.session_dict["projects"]],]
        # check entries with same name
        for entries in [databases,plugins,projects]:
            if len(entries[1]) != len(list(set(entries[1]))):
                return f"2 or more {entries[0]} with same name exist"
        # check for non-existing entries
        for project in self.session_dict["projects"]:
            for db in project["databases"]:
                if db not in databases[1]:
                    return f"{db} database in project '{project['name']}' not in main databases list"
            for pl in project["plugins"]:
                if pl not in plugins[1]:
                    return f"{pl} plugin in project '{project['name']}' not in main plugins list"
        return 0

class Project:
    def __init__(self, project_dict):
        self.name       = project_dict["name"]
        self.databases  = project_dict["databases"]
        self.plugins    = project_dict["plugins"]

class Plugin:
    def __init__(self, plugin_dict):
        self.name       = plugin_dict["name"]
        self.ab_channel = plugin_dict["ab_channel"]
        self.version    = plugin_dict["version"]

class Database:
    def __init__(self, database_dict):
        self.name       = database_dict["name"]
        self.filename   = database_dict["filename"]
        self.location   = database_dict["location"]