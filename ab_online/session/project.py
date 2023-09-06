from .database import Database
from .plugin import Plugin


class Project:
    def __init__(
        self, name: str, databases: list[Database] = [], plugins: list[Plugin] = []
    ):
        """Describe an Activity Browser project

        :param name: project name
        :type name: str
        :param databases: databases to add to project, defaults to []
        :type databases: list[Database], optional
        :param plugins: plugins to add to project, defaults to []
        :type plugins: list[Plugin], optional
        """
        self.name: str = name  #:
        self.databases: dict[str, Database] = {}  #:
        self.plugins: dict[str, Plugin] = {}  #:

        for db in databases:
            self.add_database(db)
        for pl in plugins:
            self.add_plugin(pl)

    def add_database(self, db):
        self.databases[db.name] = db

    def add_plugin(self, plugin):
        self.plugins[plugin.name] = plugin
