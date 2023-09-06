
class Plugin:
    def __init__(self, name: str, channel: str, version: str):
        """Describe an Activity Browser plugin

        :param name: plugin conda package name
        :type name: str 
        :param channel: anaconda package channel
        :type channel: str
        :param version: conda package version
        :type version: str
        """
        self.name: str       = name     #:
        self.channel: str    = channel  #:
        self.version: str    = version  #: