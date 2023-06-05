import os

import appdirs

class DataController:

    def __init__(self):
        
        

        self.settings_dir = appdirs.AppDirs("ActivityBrowserOnline", "ActivityBrowserOnline")
        if not os.path.isdir(self.settings_dir.user_data_dir):
            os.makedirs(self.settings_dir.user_data_dir, exist_ok=True)

    def get_default_settings(cls) -> dict:
        """ Using methods from the commontasks file to set default settings
        """
        return {
            "current_bw_dir": cls.get_default_directory(),
            "custom_bw_dirs": [cls.get_default_directory()],
            "startup_project": cls.get_default_project_name(),
        } 