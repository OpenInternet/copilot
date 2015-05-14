import os
from urlparse import urlparse
from copilot.utils.file_sys import get_usb_dirs
from ConfigParser import SafeConfigParser
from copilot.utils.plugin import Plugin, is_plugin, get_plugins

#stat logging
import logging
log = logging.getLogger(__name__)


def get_config_dir(directory):
    directories = {"main" : "/tmp/copilot/",
                   "profiles" : "/tmp/copilot/profiles",
                   "temporary" : "/tmp/copilot/tmp/"}
    plugins = get_value_dict("directory")
    for p in plugins:
        directories[p] = plugins[p][0]
    if _dir in directories:
        log.debug("Directory {0} found and being returned.".format(_dir))
        return directories[_dir]
    else:
        raise ValueError("That config directory is not valid.")

def get_config_file(config):
    """ return the path to a config file."""
    directory = get_option("directory", config)[0]
    config_file = get_option("config_file", config)[0]
    path = os.path.join(directory, config_file)

def get_valid_actions(package=None):
    """ Returns the valid actions for a package, or all packages as a list"""
    if not package:
        return get_unique_values("actions")
    else:
        return get_option("actions", package)

def get_valid_targets():
    return get_unique_values("target")

def get_config_writer(name):
    """
    Get a plugins config writer object
    """
    if not is_plugin(name):
        raise ValueError("{0} is not a plugin.".format(name))
    plugin = Plugin(name)
    writer = plugin.get_config_writer()
    return writer

def get_option(option, plugin):
    """Get an option from a plugin config file as a list."""
    if not is_plugin(plugin):
        raise ValueError("{0} is not a plugin.".format(plugin))
    plugin = PluginConfig(plugin)
    return plugin.data['info'][option]

def get_unique_values(option):
    """Returns a list of a specific key's value across all plugins config files with no repeats."""
    values = []
    val_list = get_value_list(option)
    for i in val_dict:
        # All values are returned as a list
        for j in i:
            if j not in values:
                values.append(j)
    return values

def get_value_list(option):
    """Returns a list of (plugin,[value1, value2, value3]) tuples of a specific key's value across all plugins config files."""
    plugins = get_plugins
    plist = []
    for p in plugins:
        _plugin = PluginConfig(p)
        plist.append((p, _plugin.data['info'][option]))
    return plist

def get_value_dict(option):
    """Returns a dictionary of {plugin: [value1, value2, value3]} of a specific key's value across all plugins config files."""
    plugins = get_plugins
    pdict = {}
    for p in plugins:
        _plugin = PluginConfig(p)
        pdict[p] = _plugin.data['info'][option]
    return pdict

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
        except:
            log.warn("Config file at {0} is not properly configured. Marking as invalid.".format(self.path))
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
        except:
            log.warn("Config file at {0} is not properly configured. Marking as invalid.".format(self.path))
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


class PluginConfig(object):
    def __init__(self, name):
        self.path = os.path.abspath(os.path.join("./", name, "plugin.conf"))
        self.parser = ProfileParser()
        if self.valid():
            self.data = self.build_map()

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

    def valid(self):
        try:
            _data = self.parser.read(self.path)
        except:
            log.warn("Config file at {0} is not properly configured. Marking as invalid.".format(self.path))
            return False
        if _data == []:
            log.warn("Config file at {0} is not properly configured or does not exist. Marking as invalid.".format(self.path))
            return False
        required = ["name", "config_file", "target", "actions", "directory"]
        for r in required:
            if not self.parser.has_option("info", r):
                log.warn("Config file at {0} has no {1} and therefore cannot be used. Marking as invalid.".format(self.path, r))
                return False
        log.info("Config file at {0} is properly formatted. Marking as valid.".format(self.path))
        return True
