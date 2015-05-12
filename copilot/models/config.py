import os
from urlparse import urlparse
from copilot.utils.file_sys import get_usb_dirs
from ConfigParser import SafeConfigParser
#stat logging
import logging
log = logging.getLogger(__name__)

"""
CP_PACKAGES = { "SERVICE NAME" : {
                   "name" : "SERVICE NAME",
                   "config_file": "CONFIG FILE NAME",
                   "target" : "TARGET NAME",
                   "actions": ["ACTION 001", "ACTION 002", "ACTION ETC"],
                   "directory":"DIRECTORY HEADING FROM CP_DIRS VAR"}
"""
#TODO Remove this variable and pull package configs from some sort of config file
CP_PACKAGES = {"dnschef":{"name": "dnschef",
                          "config_file": "dnschef.conf",
                          "target" : "dns",
                          "actions": ["block", "redirect"],
                          "directory":"main"},
               "create_ap":{"name": "create_ap",
                     "config_file": "ap.conf",
                     "directory":"main"}}

def get_config_dir(directory):
    directories = {"main" : "/tmp/copilot/",
                   "profiles" : "/tmp/copilot/profiles",
                   "temporary" : "/tmp/copilot/tmp/"}
    if directory in directories:
        log.debug("Directory {0} found and being returned.".format(directory))
        return directories[directory]
    else:
        raise ValueError("That config directory is not valid.")

def get_config_file(config):
    """ return the path to a config file."""
    _copilot_dir = get_config_dir("main")
    if config in CP_PACKAGES:
        if "config_file" in CP_PACKAGES[config]:
            try:
                _directory = get_config_dir(CP_PACKAGES[config]["directory"])
                _path = os.path.join(_directory, CP_PACKAGES[config]["config_file"])
                log.debug("Returning config path {0}".format(_path))
                return _path
            except ValueError as err:
                log.error("Directory found in CP_PACKAGES under the {0} package was invalid.".format(config))
                raise ValueError(err)
    else:
        raise ValueError("That config file is not valid.")

def get_valid_actions(package=None):
    if not package:
        _valid_actions = ["block", "redirect"]
    else:
        for item in CP_PACKAGES:
            if "target" in CP_PACKAGES[item] and "target" == package:
                _valid_actions = CP_PACKAGES[item]["actions"]
    return _valid_actions

def get_valid_targets():
    _targets = []
    for item in CP_PACKAGES:
        if "target" in CP_PACKAGES[item]:
            _targets.append(CP_PACKAGES[item]["target"])
    return _targets


class Config(object):

    def __init__(self):
        self._rules = []
        self.config_dir = "main"

    @property
    def config_type(self):
        return self._config_type

    @config_type.setter
    def config_type(self, config_type):
        try:
            config_file = get_config_file(config_type)
        except ValueError as err:
            log.error("An invalid config type was passed. Please check \"get_config_file\" in the models/config.py scripts for the valid types of config files.")
            raise ValueError(err)
        self._config_type = config_type
        self.config_file = config_file

    def check_file(self):
        if os.path.exists(self._config_file):
            return True
        else:
            return False

    def add_rule(self, rule):
        log.debug("adding rule {0}".format(rule))
        self._rules.append(rule)

    def write(self):
        self.prepare()
        log.debug("Opening config file {0} for writing.".format(self.config_file))
        with open(self.config_file, 'w+') as config_file:
            self.write_header(config_file)
            for rule in self._rules:
                self.write_rule(config_file, rule)

    def prepare(self):
        log.info("Creating the config directory if it does not exist.")
        _dir = get_config_dir(self.config_dir)
        if not os.path.exists(_dir):
            log.info("Creating the main config directory {0}.".format(_dir))
            os.makedirs(_dir)
        else:
            log.info("The config directory {0} exists and will not be created.".format(_dir))

    def write_rule(self, config_file, rule):
        log.debug("writing rule {0}".format(rule))
        config_file.write(rule)

    def write_header(self, config_file):
        log.debug("writing header info {0}".format(self.header))
        if self.header:
            log.debug("Found header. Writing to config file {0}".format(config_file))
            config_file.write(self.header)
        else:
            log.debug("No header found.")

class APConfig(Config):

    def __init__(self, ap_name, ap_password, iface_in="eth0", iface_out="wlan0"):
        super(APConfig, self).__init__()
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


class ProfileParser(SafeConfigParser):
    def get_list(self,section,option):
        value = self.get(section,option)
        return list(filter(None, (x.strip() for x in value.splitlines())))

class ProfileWriter(ProfileParser):
    def set_rule(self, rule):
        action = rule[0]
        target = rule[1]
        sub = rule[2]
        rule_list = []
        if not self.has_section(action):
            self.add_section(action)
        if self.has_option(action, target):
            rule_list = self.get_list(action, target)
        rule_list.append(sub)
        text_rules = "\n\t".join(rule_list)
        self.set(action, target, text_rules)


class ProfileConfig(object):
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.parser = ProfileParser()
        if self.valid():
            self.data = self.build_map()
        self.rules = self.get_rules()

    def get_rules(self):
        """
        Returns a list of rules.
        [["block", "dns", "www.internews.org"],["redirect", "dns", "info.internews"]]
        """
        rules = []
        _val_targets = get_valid_targets()
        for target in self.data:
            if target in _val_targets:
                for action in self.data[target]:
                    if action in get_valid_actions(target):
                        for sub in self.data[target][action]:
                            rules.append([action, target, sub])
        return rules

    def valid(self):
        try:
            _data = self.parser.read(self.path)
        except as e:
            log.warn("Config file at {0} is not properly configured. Marking as invalid.".format(self.path))
            log.debug(e)
            return False
        if _data == []:
            log.warn("Config file at {0} is not properly configured or does not exist. Marking as invalid.".format(self.path))
            return False
        if not self.parser.has_option("info", "name"):
            log.warn("Config file at {0} has no name and therefore cannot be used. Marking as invalid.".format(self.path))
            return False
        #TODO Add config file format values for each module
        log.info("Config file at {0} is properly formatted. Marking as valid.".format(self.path))
        return True

    def build_map(self):
        _dict = {}
        _data = self.parser.read(self.path)
        _sections = self.parser.sections()
        log.debug("Config file has the following sections {0}.".format(_sections))
        for sect in _sections:
            _dict[sect] = {}
            _options = self.parser.options(sect)
            log.debug("Config file section {0} has the following options {0}.".format(sect, _options))
            for opt in _options:
                _dict[sect][opt] = self.parser.getlist("sect", "opt")
        return _dict
