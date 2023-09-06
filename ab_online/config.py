import appdirs
import pkg_resources

# These are the default settings of Activity Browser Online.
# They can be changed using global arguments when running
# ab_online.ab (see help for arguments description)

STORAGE = appdirs.user_data_dir("ActivityBrowserOnline")
DEBUG = False
INCLUDES = pkg_resources.resource_filename(__name__, "includes")
DOMAIN = "localhost"
DEV = False
