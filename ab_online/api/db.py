from ..controllers import Storage
from .. import config as CONFIG


class db:
    @staticmethod
    def list(verbose=False, extension=False):
        """list existing databases

        :param verbose: show infos about database, defaults to False
        :type verbose: bool, optional
        :param extension: show files extension, defaults to False
        :type extension: bool
        """
        return Storage.list_files("databases", extension=extension)

    @staticmethod
    def add(
        file: str,
        name: str,
        link: bool = False,
        force: bool = False,
        format: str = "bw2package",
    ):
        """Add a database to AB-Online

        :param file: path to the database file
        :type file: str
        :param name: name to give to the file
        :type name: str
        :param link: create a link instead of copying file, defaults to False
        :type link: bool, optional
        :param force: override file with same name, defaults to False
        :type force: bool, optional
        :param format: only bw2package format is currently supported, defaults to "bw2package"
        :type format: str, optional
        """
        if CONFIG.SERVER_MODE:
            link = request.args.get("link", default=False, type=bool)
            force = request.args.get("force", default=False, type=bool)
        Storage.add_file(file, name, folder="databases",
                         force=force, link=link)

    @staticmethod
    def remove(name: str):
        """Remove a database from AB-Online

        :param name: name of file (without extension)
        :type name: str
        """
        Storage.delete_file(f"databases/{name}")

    @staticmethod
    def update(database: str, file: str, link: bool = False):
        """replace database by new file

        :param database: name of the database to update
        :type database: str
        :param file: new database file path
        :type file: str
        :param link: create a link instead of copying file, defaults to False
        :type link: bool, optional
        """
        Storage.add_file(
            file=file, name=database, folder="databases", force=True, link=link
        )
