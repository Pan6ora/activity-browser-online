import json
from ..session import Session
from .. import config


class Machine:
    """This class is meant to be used from a machine docker container"""

    @classmethod
    def setup_session(cls, session_file):
        import brightway2 as bw
        from bw2io.package import BW2Package

        session = Session(session_file)

        default_exist = False
        # create and setup projects
        for project in session.projects.values():
            # create project
            bw.projects.set_current(project.name)
            # add databases
            for database in project.databases:
                filename = session.databases[database].filename
                BW2Package().import_file(f"{config.STORAGE}/databases/{filename}")
            # add plugins and databases to AB settings
            settings = {}
            settings["plugins_list"] = []
            settings["read-only-databases"] = {}
            for plugin in project.plugins:
                settings["plugins_list"].append(f"ab_plugin_{plugin}")
            for db in bw.databases:
                settings["read-only-databases"][db] = True
            json_object = json.dumps(settings, indent=4)
            with open(f"{bw.projects.dir}/AB_project_settings.json", "w") as f:
                f.write(json_object)
            # default project exist, do not remove it
            if project.name == "default":
                default_exist = True
            # add default flows and methods
            bw.bw2setup()

        if not default_exist:
            bw.projects.delete_project("default", delete_dir=True)
        # set default project
        ABsettings = {
            "current_bw_dir": "/home/mambauser/.local/share/Brightway3",
            "custom_bw_dirs": ["/home/mambauser/.local/share/Brightway3"],
            "startup_project": list(session.projects.keys())[0],
        }
        json_object = json.dumps(ABsettings, indent=4)
        with open(
            "/home/mambauser/.local/share/ActivityBrowser/ABsettings.json", "w"
        ) as f:
            f.write(json_object)
