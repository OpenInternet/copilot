import os
import string
import importlib
from urlparse import urlparse
from copilot.utils.file_sys import get_usb_dirs, get_likely_usb
from ConfigParser import SafeConfigParser
from copilot.utils.plugin import is_plugin, get_plugins

#stat logging
import logging
log = logging.getLogger(__name__)


def get_config_dir(directory):
    directories = {"main" : "/tmp/copilot/",
                   "profiles" : "/var/lib/copilot/profiles/",
                   "temporary" : "/tmp/copilot/tmp/"}
    # Adding plugin directories
    plugins = get_value_dict("directory")
    for p in plugins:
        directories[p] = plugins[p][0]
    # Adding USB directory
    directories["usb"] = get_likely_usb()
    if directory in directories:
        log.debug("Directory {0} found and being returned.".format(directory))
        return directories[directory]
    else:
        raise ValueError("That config directory is not valid.")

def get_config_file(config):
    """ return the path to a config file."""
    log.info("getting {0} config file.".format(config))
    directory = get_option("directory", config)[0]
    log.debug("found directory {0}".format(directory))
    config_file = get_option("config_file", config)[0]
    log.debug("found config file {0}".format(config_file))
    path = os.path.join(directory, config_file)
    return path

def get_valid_actions(package=None):
    """ Returns the valid actions for a package, or all packages as a list"""
    if not package:
        return get_unique_values("actions")
    else:
        return get_option("actions", package)

def get_valid_targets():
    log.info("getting valid targets.")
    return get_unique_values("target")

def get_config_writer(name):
    """
    Get a plugins config writer object
    """
    log.info("getting a plugins config writer.")
    if not is_plugin(name):
        raise ValueError("{0} is not a plugin.".format(name))
    config = importlib.import_module('copilot.plugins.{0}.config'.format(name))
    log.debug("{0} contains {1}".format(config.__name__, dir(config)))
    writer = config.ConfigWriter()
    return writer

def get_option(option, plugin):
    """Get an option from a plugin config file as a list."""
    log.info("getting option {0} from {1}'s config file.".format(option, plugin))
    if not is_plugin(plugin):
        raise ValueError("{0} is not a plugin.".format(plugin))
    plugin = PluginConfig(plugin)
    if plugin.valid():
        try:
            option_found = plugin.data['info'][option]
            log.debug("returning {0} option.".format(option_found))
            return option_found
        except KeyError as err:
            log.warning("Plugin {0} does not have a {1} key.".format(p, option))
            return []
    else:
        return []

def get_unique_values(option):
    """Returns a list of a specific key's value across all plugins config files with no repeats."""
    log.info("getting all unique values for option {0}.".format(option))
    values = []
    val_list = get_value_dict(option)
    for plugin in val_list:
        # All values are returned as a list
        for j in val_list[plugin]:
            if j not in values:
                values.append(j)
    log.debug("unique values found: {0}".format(values))
    return values

def get_value_list(option):
    """Returns a list of (plugin,[value1, value2, value3]) tuples of a specific key's value across all plugins config files."""
    log.info("Getting a list of all values")
    plugins = get_plugins()
    plist = []
    for p in plugins:
        _plugin = PluginConfig(p)
        if _plugin.valid():
            try:
                plist.append((p, _plugin.data['info'][option]))
            except KeyError as err:
                log.warning("Plugin {0} does not have a {1} key.".format(p, option))
    log.debug("values found: {0}".format(plist))
    return plist

def get_value_dict(option):
    """Returns a dictionary of {plugin: [value1, value2, value3]} of a specific key's value across all plugins config files."""
    log.info("Getting a dict of all values")
    plugins = get_plugins()
    pdict = {}
    for p in plugins:
        _plugin = PluginConfig(p)
        if _plugin.valid():
            try:
                pdict[p] = _plugin.data['info'][option]
            except KeyError as err:
                log.warning("Plugin {0} does not have a {1} key.".format(p, option))
    log.debug("values found: {0}".format(pdict))
    return pdict

def get_target_by_actions():
    log.info("getting targets (e.g. plugins) sorted by actions")
    tar_act_dict = {}
    tdict = get_value_dict("actions")
    for target in tdict:
        for action in tdict[target]:
            if action not in tar_act_dict:
                tar_act_dict[action] = []
                tar_act_dict[action].append(target)
            elif target not in tar_act_dict[action]:
                tar_act_dict[action].append(target)
            else:
                log.debug("Found action {0} in target {1}. This should not occur. A plugin is being examed twice or is somehow duplicated.".format(action, target))
    log.debug("target/action pairs found: {0}".format(tar_act_dict))
    return tar_act_dict


class Config(object):

    def __init__(self):
        self._rules = []
        self.config_dir = "main"

    @property
    def config_type(self):
        try:
            return self._config_type
        except AttributeError as err:
            log.debug("Config type is not yet set, returning empty string.")
            return ""

    @config_type.setter
    def config_type(self, config_type):
        try:
            config_file = get_config_file(config_type)
            log.debug("config file {0} found".format(config_file))
        except ValueError as err:
            log.error("An invalid config type was passed. Please check \"get_config_file\" in the models/config.py scripts for the valid types of config files.")
            raise ValueError(err)
        log.debug("setting config type.")
        self._config_type = config_type
        log.debug("setting config file {0}.".format(config_file))
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
        if not self.has_section(target):
            self.add_section(target)
        if self.has_option(target, action):
            rule_list = self.get_list(target, action)
        rule_list.append(sub)
        text_rules = "\n\t".join(rule_list)
        self.set(target, action, text_rules)

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
        log.debug("Found rules: {0}".format(rules))
        return rules

    def valid(self):
        try:
            _data = self.parser.read(self.path)
        except:
            log.debug("Config file at {0} is not properly configured. Marking as invalid.".format(self.path))
            return False
        if _data == []:
            log.debug("Config file at {0} is not properly configured or does not exist. Marking as invalid.".format(self.path))
            return False
        if not self.parser.has_option("info", "name"):
            log.debug("Config file at {0} has no name and therefore cannot be used. Marking as invalid.".format(self.path))
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
                _dict[sect][opt] = self.parser.get_list(sect, opt)
        return _dict




class PluginConfig(object):
    def __init__(self, name):
        self.path = os.path.abspath(os.path.join("/home/www/copilot/copilot/plugins/", name, "plugin.conf"))
        self.parser = ProfileParser()
        if self.valid():
            self.data = self.build_map()

    def build_map(self):
        _dict = {}
        _data = self.parser.readfp(open(self.path))
        _sections = self.parser.sections()
        log.debug("Config file has the following sections {0}.".format(_sections))
        for sect in _sections:
            _dict[sect] = {}
            log.debug("getting options for section {0}".format(sect))
            _options = self.parser.options(sect)
            log.debug("It has the following options {0}.".format(_options))
            for opt in _options:
                _dict[sect][opt] = self.parser.get_list(sect, opt)
        log.debug("Created below plugin data map. \n {0}".format(_dict))
        return _dict

    def valid(self):
        try:
            _data = self.parser.read(self.path)
        except:
            log.info("Config file at {0} is not properly configured. Marking as invalid.".format(self.path))
            return False
        if _data == []:
            log.info("Config file at {0} is not properly configured or does not exist. Marking as invalid.".format(self.path))
            return False
        required = ["name", "config_file", "directory"]
        desired = ["target", "actions"]
        for r in required:
            if not self.parser.has_option("info", r):
                log.info("Config file at {0} has no {1} and therefore cannot be used. Marking as invalid.".format(self.path, r))
                return False
        for r in desired:
            if not self.parser.has_option("info", r):
                log.info("Config file at {0} has no {1} and will not generate rules.".format(self.path, r))
        log.info("Config file at {0} is properly formatted. Marking as valid.".format(self.path))
        return True
