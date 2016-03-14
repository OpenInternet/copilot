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


def import_plugin(name):
    """Import and return a plugin module

    Args:
        name (str): The name of the plugin that you want a writer for.
    """

    log.info("getting a plugins configuration.")
    # Get plugin directory from system COPIOT_PLUGINS_DIRECTORY
    plugin_dir = os.environ['COPILOT_PLUGINS_DIRECTORY']
    log.debug("Plugin directory identified at {0}".format(plugin_dir))
    if plugin_dir not in sys.path:
        sys.path.append(plugin_dir)
    log.debug("After adding plugin_dir python path is: {0}".format(sys.path))

    if not is_plugin(name):
        raise ValueError("{0} is not a plugin.".format(name))
    try:
        plugin_config_path = "plugins.{0}.config".format(name)
        log.debug("importing library from {0}".format(plugin_config_path))
        config = importlib.import_module(plugin_config_path)
    except ImportError as _e:
        log.error("Could not import plugin {0}".format(name))
        log.error(_e)
        raise ImportError(_e)
    log.debug("returning {0}".format(config.__name__))
    return config

def get_plugin(name):
    """Get a plugins copilot configuration object

    Args:
        name (str): The name of the plugin that you want a writer for.
    """

    plugin = import_plugin(name)
    config = plugin.Plugin()
    log.debug("Plugin {0} imported.".format(name))
    return config

def get_config_writer(name):
    """Get a plugins config file writer object.

    Args:
        name (str): The name of the plugin that you want a writer for.
    """
    log.debug("getting configuration writer")
    plugin = import_plugin(name)
    writer = plugin.ConfigWriter()
    return writer

def get_config_dir(directory):
    """Return the appropriate directory for a non-plugin config file.

    Each type of config file is kept in a different location. This
    function identified the correct location for a specific config
    file.

    Args:
        directory (str): The type of config file directory to return.
    """
    log.debug("requesting config directory {0}".format(directory))
    base_directories = {}
    base_directories.setdefault("profiles", os.environ['COPILOT_PROFILE_CONFIG_DIRECTORY'])
    base_directories.setdefault("temporary", os.environ['COPILOT_TEMPORARY_CONFIG_DIRECTORY'])
    base_directories.setdefault("main", os.environ['COPILOT_DEFAULT_CONFIG_DIRECTORY'])
    log.debug("base directories set as {0}".format(base_directories))
    # Test if one of the basic directories
    if directory in base_directories:
        log.debug("directory {0} found in the base directories".format(directory))
        return base_directories.get(directory)
    elif directory == "usb":
        log.debug("directory is a usb directory")
        return get_likely_usb()
    else:
        log.error("The config directory {0} is not valid.".format(directory))
        raise ValueError("That config directory is not valid.")

def get_config_path(plugin_name):
    """ Return the path to a plugins config file.

    TODO Rename to get_config_path

    Given a plugins name this function will query the
    plugins options to retreive the path where its
    config file should be stored.

    Args:
        plugin_name (str): The name of the plugin that you wish to retrive a
    config path for.
    """
    log.info("getting {0}'s config path.".format(plugin_name))
    plugin = get_plugin(plugin_name)
    return plugin.config_path

def import_all_plugins():
    """Create a list containing all plugin objects.
    """
    log.debug("importing all plugins")
    plugin_names = get_plugins()
    plugins = []
    for name in plugin_names:
        plugins.append(get_plugin(name))
    return plugins

def get_valid_actions(plugin_name=None):
    """ Returns the valid actions for a plugin, or all plugin as a list"""
    if not plugin_name:
        plugins = import_all_plugins()
        combined_values = set()
        for plugin in plugins:
            combined_values.union(plugin.actions)
        return combined_values
    else:
        return get_plugin(plugin_name).actions

def get_valid_targets(plugin_name=None):
    """Return all valid targets for CoPilot Rules."""
    log.info("getting valid targets.")
    if not plugin_name:
        plugins = import_all_plugins()
        combined_values = set()
        for plugin in plugins:
            combined_values.union(plugin.targets)
        return combined_values
    else:
        return get_plugin(plugin_name).targets

def get_plugins_with_subtargets():
    """Create a set containing all possible targets that have subtargets.
    """
    log.debug("Getting plugins with subtargets")
    plugins = import_all_plugins()
    has_subtarget = set()
    for plugin in plugins:
        if plugin.has_subtarget is True:
            log.debug("plugin {0} has subtargets".format(plugin.name))
            has_subtarget.add(plugin.name)
    return has_subtarget

def get_targets_with_subtargets():
    """Create a set containing all possible targets that have subtargets.
    """
    log.debug("Getting targets with subtargets")
    plugins = get_plugins_with_subtargets()
    targets = set()
    for plugin_name in plugins:
        targets.union(get_plugin(plugin_name).targets)
    return targets

def get_plugin_from_rules(action, target):
    plugins = import_all_plugins()
    identified_plugins = set()
    for plugin in plugins:
        if action in plugin.actions:
            log.debug("Plugin {0} has the action".format(plugin.name))
            if target in plugin.targets:
                log.debug("Plugin {0} has the target".format(plugin.name))
                identified_plugins.add(plugin.name)

    log.debug("Plugins found = {0}".format(identified_plugins))
    if len(identified_plugins) == 1:
        identified_plugin = plugins.pop()
        log.info("Plugin {0} identified as target plugin.".format(identified_plugin))
        return identified_plugin
    elif len(identified_plugins) > 1:
        identified_plugin = plugins.pop()
        log.warn("Multiple plugins found that support the rule pair" +
                 "{0} : {1}. This is not allowed.".format(action, target) +
                 " Using first plugin: {2}".format(identified_plugin))
        return identified_plugin
    else:
        log.warn("No plugins found that matched the " +
                 "{0}:{1} rule pair.".format(action, target))
        raise ValueError("No plugins found that matched the " +
                         "{0}:{1} rule pair.".format(action, target))

def get_target_by_actions():
    """Get a dict of targets sorted by their available actions.

    Get a dictionary keyed with available actions (The censorship/surveillance
    action to be taken against the "targeted" traffic. Examples would
    be to block, throttle, redirect, or monitor.) with values containing
    lists of all the possile targets (The type of network traffic to be targeted
    by the co-pilot.) that the action can be used against.
    """
    log.info("getting all plugins targets sorted by actions")
    plugins = import_all_plugins()
    collective_rules = {}
    for plugin in plugins:
        rules = plugin.rules
        if rules is None:
            continue

        for action, targets in rules.iteritems():
            log.debug("Plugin {0} has action {1} ".format(plugin.name, action) +
                      "on targets {2}".format(targets))
            collective_rules.setdefault(action, set()).union(targets)

    log.debug("action to target sets found: {0}".format(collective_rules))
    return collective_rules


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
            config_file = get_config_path(config_type)
            log.debug("config file {0} found".format(config_file))
        except ValueError as err:
            log.error("An invalid config type was passed. Please check \"get_config_path\" in the models/config.py scripts for the valid types of config files.")
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

        log.info("Creating the config directory " +
                 "{0} if it does not exist.".format(self.config_dir))
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
        try:
            self.rules = self.get_rules()
        except AttributeError:
            raise ValueError("Config file may be properly formatted but " +
                             " the rules found in the config seem to be corrupted.")

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
                    plugin_name = get_plugin_from_rules(action, target)
                    if action in get_valid_actions(plugin_name):
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
            log.debug("Config file section {0} has the following options {1}.".format(sect, _options))
            for opt in _options:
                _dict[sect][opt] = self.parser.get_list(sect, opt)
        return _dict

class PluginOptions(object):
    """Plugin options object."""

    def __init__(self):
        """

        A Plugin requires the following values to be set during its initialization.

        self.rules = {"block":set(["dns"]),
                      "redirect":set(["dns"])}
        # self.rules should equal None if a plugin has no rules.
        self.name = "dnschef"
        self.has_subtarget = True
        self.config_directory = "/tmp/copilot/"
        self.config_file = "dnschef.conf"
        self.config_path = path.join(self.config_directory, self.config_file)

        TODO:
                advanced_configuration_page = bool

        """
        log.debug("Initializing base plugin object")
        self.rules = {}
        self.name = None
        self.config_file = None
        self.has_subtarget = None
        self.config_directory = None
        self.config_path = None

    @property
    def actions(self):
        """Returns a set containing the plugins actions."""
        if self.rules is None:
            return set([])
        else:
            return set(self.rules.keys())

    @property
    def targets(self):
        """Returns a set containing the plugins targets."""
        if self.rules is None:
            return set([])
        else:
            targets = set()
            for target in self.rules.values():
                targets.union(target)
            return targets

    def get_actions(self, target=None):
        """Get a list of actions corresponding to a target.
        """
        if self.rules is None:
            return []
        actions = set()
        if target:
            for action_name, targets in self.rules.iteritems():
                if target in targets:
                    actions.add(action_name)
        else:
            return self.actions

    def get_targets(self, action=None):
        """Get a list of targets corresponding to an action.
        """
        if self.rules is None:
            return []
        if action:
            for action_name, targets in self.rules.iteritems():
                if action == action_name:
                    return list(targets)
        else:
            return self.targets

    def has_action(self, action):
        if action in self.actions:
            return True
        else:
            return False

    def has_targets(self, target):
        if target in self.targets:
            return True
        else:
            return False
