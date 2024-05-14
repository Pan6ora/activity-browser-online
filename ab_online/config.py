import appdirs
import pkg_resources

# These are the default settings of Activity Browser Online.
# They can be changed using global arguments when running
# ab_online.ab (see help for arguments description)

STORAGE = appdirs.user_data_dir(
    "ActivityBrowserOnline")  # app storage location
DEBUG = False  # print debug logs
INCLUDES = pkg_resources.resource_filename(
    __name__, "includes"
)  # app includes location
DOMAIN = "ab-online.localhost"  # web url
DEV = False  # use current folder code instead of ab-online app when building docker
SERVER_MODE = False  # used in the API
