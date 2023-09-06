
class Database:
    def __init__(self, name: str, filename: str, location: str):
        """Describe a bw2package database

        :param name: database display name
        :type name: str
        :param filename: database file name
        :type filename: str
        :param location: path to database folder
        :type location: str
        """
        self.name: str       = name          #:
        self.filename: str   = filename      #:
        self.location: str   = location      #: