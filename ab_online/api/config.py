import json
from ..controllers import Storage
from .. import config as CONFIG


class config:

    @staticmethod
    def update(domain=""):
        if domain:
            CONFIG.DOMAIN = domain
        config.write_settings()

    @staticmethod
    def read_settings():
        with open(f"{CONFIG.STORAGE}/settings.json") as f:
            result_dict = json.load(f)
            CONFIG.DOMAIN = result_dict["domain"]

    @staticmethod
    def write_settings():
        settings = {"domain": CONFIG.DOMAIN}
        json_object = json.dumps(settings, indent=4)
        with open(f"{CONFIG.STORAGE}/settings.json", "w") as f:
            f.write(json_object)
