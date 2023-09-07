import os
import pkg_resources
import shutil
import json

from .. import config


class Storage:
    @classmethod
    def create_folder(cls, path):
        os.makedirs(f"{config.STORAGE}/{path}", exist_ok=True)

    @classmethod
    def delete_folder(cls, path):
        shutil.rmtree(f"{config.STORAGE}/{path}", ignore_errors=True)

    @classmethod
    def delete_file(cls, path):
        os.remove(f"{config.STORAGE}/{path}")

    @classmethod
    def add_file(cls, file, name, folder="", force=False, link=False):
        """import a file to the data folder

        :param file: path of the file to import
        :type file: str
        :param name: name of the destination
        :type name: str
        :param force: replace existing file, defaults to False
        :type force: bool, optional
        :param link: create a link instead of copying, defaults to False
        :type link: bool, optional
        """
        dest = f"{config.STORAGE}/{folder}/{name}"
        if force or not os.path.isfile(dest):
            if not link:
                shutil.copyfile(file, dest)
            else:
                os.symlink(file, dest)

    @classmethod
    def list_files(cls, folder="", extension=True):
        """return a list of files in folder

        :param folder: path within storage, defaults to ""
        :type folder: str, optional
        :param extension: show files extension, defaults to False
        :type extension: bool, optional
        """
        path = f"{config.STORAGE}/{folder}"
        if extension:
            return os.listdir(path)
        else:
            return [os.path.splitext(filename)[0] for filename in os.listdir(path)]

    @classmethod
    def read_json(cls, file: str):
        """Convert json file to python dict

        :return: a new dictionary with json content
        :rtype: dict
        """
        with open(file) as f:
            result_dict = json.load(f)
            return result_dict

    @classmethod
    def init_storage(cls):
        cls.create_folder("")
        cls.create_folder("sessions")
        cls.create_folder("databases")
        cls.create_folder("sessions_storage")
        cls.create_folder("proxy")
        cls.add_file(
            f"{config.INCLUDES}/example_session.json", "example.json", "sessions"
        )
        cls.add_file(f"{config.INCLUDES}/.dockerignore", ".dockerignore", "")
        cls.add_file(
            f"{config.INCLUDES}/databases/biosphere3.bw2package",
            "biosphere3.bw2package",
            "databases",
        )
        cls.add_file(
            f"{config.INCLUDES}/databases/Idemat.bw2package",
            "Idemat.bw2package",
            "databases",
        )
        cls.add_file(
            f"{config.INCLUDES}/Dockerfile_machine",
            "Dockerfile_machine",
            "",
            force=True,
        )