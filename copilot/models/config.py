import os, sys
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
    """Return the appropriate directory for a type of config file.

    Each type of config file is kept in a different location. This
    function identified the correct location for a specific config
    file.

    Args:
        directory (str): The type of config file directory to return.
    """

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
    """ Return the path to a plugins config file.

    Given a plugins name this function will query the
    plugins options to retreive the path where its
    config file should be stored.

    Args:
        config (str): The name of the plugin that you wish to retrive a
    config path for.
    """
    log.info("getting {0} config file.".format(config))
    directory = get_option("directory", config)[0]
    log.debug("found directory {0}".format(directory))
    config_file = get_option("config_file", config)[0]
    log.debug("found config file {0}".format(config_file))
    path = os.path.join(directory, config_file)
    return path

def get_valid_actions(package=None):
    """ Returns the valid actions for a plugin, or all plugin as a list"""

    if not package:
        return get_unique_values("actions")
    else:
        return get_option("actions", package)

def get_valid_targets():
    """Return all valid targets for CoPilot Rules."""
    log.info("getting valid targets.")
    return get_unique_values("target")

def get_config_writer(name):
    """Get a plugins config file writer object.

    Args:
        name (str): The name of the plugin that you want a writer for.
    """

    log.info("getting a plugins config writer.")
    # Get plugin directory from system COPIOT_PLUGINS_DIRECTORY
    plugin_dir = os.environ['COPILOT_PLUGINS_DIRECTORY']
    sys.path.append(plugin_dir)

    if not is_plugin(name):
        raise ValueError("{0} is not a plugin.".format(name))
    config = importlib.import_module('plugins.{0}.config'.format(name))
    log.debug("{0} contains {1}".format(config.__name__, dir(config)))
    writer = config.ConfigWriter()
    return writer

def get_option(option, plugin):
    """Get an option from a plugin config file as a list.

    Args:
        option (str): The option you want to get.
        plugin (str): The name of the plugin you want the value from.
    """

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
    """ Get all possible values for a specific option across all plugins.

    Returns a list of a specific key's value across all plugins config files
    with no repeats.

    Args:
        option (str): The option you want to get unique values for.
    """

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
    """ Get a list containing the value of an option for each plugin.

    Returns a list of (plugin,[value1, value2, value3]) tuples of a
    specific key's value across all plugins config files.

    Args:
        option (str): The option you want to get values for.
    """

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

def get_plugin_from_rules(action, target):
    """ Get a plugin name from an action & target rule pair.
    """
    log.info("Obtaining plugin name from rule pair" +
             "{0} : {1}".format(action, target))
    all_actions = get_value_dict("actions")
    all_targets = get_value_dict("target")
    plugins = set()

    for plugin_name, actions in all_actions.items():
        if action in actions:
            log.debug("Plugin {0} has the action".format(plugin_name))
            if target in all_targets.get(plugin_name, []):
                log.debug("Plugin {0} has the target".format(plugin_name))
                plugins.add(plugin_name)
                log.info("Plugin {0} contained the rule pair.".format(plugin_name))

    log.debug("Plugins found = {0}".format(plugins))
    if len(plugins) == 1:
        log.info("Plugin {0} identified as target plugin.".format(plugins[0]))
        return plugins[0]
    elif len(plugins) > 1:
        log.warn("Multiple plugins found that support the rule pair" +
                 "{0} : {1}. This is not allowed.".format(action, target) +
                 " Using first plugin: {2}".format(plugins[0]))
        return plugins[0]
    else:
        log.warn("No plugins found that matched the " +
                 "{0}:{1} rule pair.".format(action, target))
        raise ValueError("No plugins found that matched the " +
                         "{0}:{1} rule pair.".format(action, target))


def get_value_dict(option):
    """Get a dict containing the value of an option for each plugin.

    Returns a dictionary of {plugin: [value1, value2, value3]} of a
    specific key's value across all plugins config files.

    Args:
        option (str): The option you want to get values for.

    """

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
    """Get a dict of targets sorted by their available actions.

    Get a dictionary keyed with available actions (The censorship/surveillance
    action to be taken against the "targeted" traffic. Examples would
    be to block, throttle, redirect, or monitor.) with values containing
    lists of all the possile targets (The type of network traffic to be targeted
    by the co-pilot.) that the action can be used against.
    """

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
    """Base config writer for plugins.

    Your plugin will have different configuration file needs than any other
    program. To handle this we have created a Python based "configuration
    writer" class that can be customized to write all manner of configuration
    files.

    Guidance for extending and modifying this config object for plugins can be
    found in the CoPilot wiki.
    https://github.com/OpenInternet/co-pilot/wiki/Plugin-Guide#minimal-configuration-example
    """

    def __init__(self):
        self._rules = []
        self.config_dir = "main"

    @property
    def config_type(self):
        """Returns the config file type."""
        try:
            return self._config_type
        except AttributeError as err:
            log.debug("Config type is not yet set, returning empty string.")
            return ""

    @config_type.setter
    def config_type(self, config_type):
        """Sets the type of the config and the location of the config file.

        Args:
            type (str): The 'type' of a configuration is an abstraction
                        of the directory that the config file is within.
        """

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
        """Checks if the config file exists."""

        if os.path.exists(self._config_file):
            return True
        else:
            return False

    def add_rule(self, rule):
        """ check, transform, and add a single rule.

        This function takes a single rule, checks if that rule is valid, transforms and formats the rule, and adds that rule to the self._rules list in a way that can be processed by the writer.

        Args:
            rule (list): A list containing the action, target, and sub-target
                of a rule as three strings.
                - action, target, sub_target = rule[0], rule[1], rule[2]
        """

        log.debug("adding rule {0}".format(rule))
        self._rules.append(rule)

    def write(self):
        """ Writes the specified config file.

        Opens, and clears the specified config file and then writes the header
        and then all of the rules for this config.
        """

        self.prepare()
        log.debug("Opening config file {0} for writing.".format(self.config_file))
        with open(self.config_file, 'w+') as config_file:
            self.write_header(config_file)
            for rule in self._rules:
                self.write_rule(config_file, rule)

    def prepare(self):
        """Create a config directory if it does not exist."""

        log.info("Creating the config directory if it does not exist.")
        _dir = get_config_dir(self.config_dir)
        if not os.path.exists(_dir):
            log.info("Creating the main config directory {0}.".format(_dir))
            os.makedirs(_dir)
        else:
            log.info("The config directory {0} exists and will not be created.".format(_dir))

    def write_rule(self, config_file, rule):
        """ Write a single rule within a config file.
        Args:
            config_file: A file handler for a config file to write to.
            rule: A string that should be written to the file.
        """

        log.debug("writing rule {0}".format(rule))
        config_file.write(rule)

    def write_header(self, config_file):
        """ Write a header at the top of a config file.
        Args:
            config_file: A file handler for a config file to write to.
        """

        log.debug("writing header info {0}".format(self.header))
        if self.header:
            log.debug("Found header. Writing to config file {0}".format(config_file))
            config_file.write(self.header)
        else:
            log.debug("No header found.")



class ProfileParser(SafeConfigParser):
    """Profile parser that can handle parsing lists."""

    def get_list(self,section,option):
        value = self.get(section,option)
        return list(filter(None, (x.strip() for x in value.splitlines())))

class ProfileWriter(ProfileParser):
    """ Object that writes basic CoPilot profiles"""

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
    """Config file parser for profiles."""

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.parser = ProfileParser()
        if self.valid():
            self.data = self.build_map()
        self.rules = self.get_rules()

    def get_rules(self):
        """ Returns a list of rules.

            [["block", "dns", "www.internews.org"],
            ["redirect", "dns", "info.internews"]]
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
        """Tests if a configuration file is properly formatted.

        Returns: (bool) True is proper, False if not
        """

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
        """ Builds a dictionary out of a config"""

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
    """ Config file parser for plugins."""

    def __init__(self, name):
        """
        Args:
            name: The plugins folder name.
        """
        plugin_base_dir = os.environ['COPILOT_PLUGINS_DIRECTORY']
        self.path = os.path.abspath(os.path.join(plugin_base_dir, "plugins", name, "plugin.conf"))
        self.parser = ProfileParser()
        if self.valid():
            self.data = self.build_map()

    def build_map(self):
        """ Builds a dictionary out of a plugin config."""

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
        """Tests if a configuration file is properly configured.

        Returns: (bool) True is proper, False if not
        """

        try:
            _data = self.parser.read(self.path)
        except:
            log.info("Config file at {0} is not ".format(self.path) +
                     "properly configured. Marking as invalid.")
            return False
        if _data == []:
            log.info("Config file at {0} is not properly ".format(self.path) +
                     "configured or does not exist. Marking as invalid.")
            return False
        required = ["name", "config_file", "directory"]
        desired = ["target", "actions"]
        for r in required:
            if not self.parser.has_option("info", r):
                log.info("Config file at {0} has no {1} and ".format(self.path, r) +
                         "therefore cannot be used. Marking as invalid.")
                return False
        for r in desired:
            if not self.parser.has_option("info", r):
                log.info("Config file at {0} has no {1} ".format(self.path, r) +
                         "and will not generate rules.")
        log.info("Config file at {0} is properly ".format(self.path) +
                 "formatted. Marking as valid.")
        return True
