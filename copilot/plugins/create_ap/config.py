from copilot.models.config import Config

import logging
log = logging.getLogger(__name__)

import string

class ConfigWriter(Config):

    def __init__(self, ap_name, ap_password, iface_in="eth0", iface_out="wlan0"):
        super(ConfigWriter, self).__init__()
        self._config_type = "create_ap"
        self.iface_in = iface_in
        self.iface_out = iface_out
        self.header = "{0} {1} ".format(self.iface_out, self.iface_in)
        self.ap_name = ap_name
        self.ap_password = ap_password
        self.add_rule(self.ap_name)
        self.add_rule(self.ap_password)
        self.config_type = "create_ap"

    @property
    def ap_password(self):
        return self._ap_password

    @ap_password.setter
    def ap_password(self, plaintext):
        if (8 < len(str(plaintext)) <= 63 and
            all(char in string.printable for char in plaintext)):
            self._ap_password = plaintext
        else:
            raise ValueError("Access Point passwords must be between 8 and 63 characters long and use only printable ASCII characters.")

    @property
    def ap_name(self):
        return self._ap_name

    @ap_name.setter
    def ap_name(self, name):
        if 0 < len(str(name)) <= 31:
            self._ap_name = name
        else:
            raise ValueError("Access Point names must be between 1 and 31 characters long.")

    def add_rule(self, rule):
        log.debug("adding rule {0}".format(rule))
        self._rules.append("{0} ".format(rule))
