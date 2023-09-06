from ..controllers import *

class db:

    def __init__(self):
        pass

    @staticmethod
    def add(self, file: str, name: str, link: bool = False,
            force: bool = False, format: str = "bw2package"):
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
        pass

    @staticmethod
    def remove(self, name: str):
        """Remove a database from AB-Online

        :param name: name of file (without extension)
        :type name: str
        """
        pass

    @staticmethod
    def update(self, database: str, file: str, link: bool = False):
        """replace database by new file

        :param database: name of the database to update
        :type database: str
        :param file: new database file path
        :type file: str
        :param link: create a link instead of copying file, defaults to False
        :type link: bool, optional       
        """
        pass