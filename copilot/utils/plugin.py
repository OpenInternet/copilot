from functools import partial
import os
import subprocess
import re
from copilot.models.config import get_value_dict

# stat logging
import logging
log = logging.getLogger(__name__)


def get_plugin_from_rules(action, target):
    """ Get a plugin name from an action & target rule pair.
    """
    log.info("Obtaining plugin name from rule pair" +
             "{0} : {1}".format(action, target))
    all_actions = get_value_dict("actions")
    all_targets = get_value_dict("target")
    plugins = []

    for plugin_name, actions in all_actions.items():
        if action in actions:
            log.debug("Plugin {0} has the action".format(plugin_name))
            if target in all_targets.get("target", []):
                log.debug("Plugin {0} has the target".format(plugin_name))
                plugins.append(plugin_name)
                log.info("Plugin {0} contained the rule pair.".format(plugin_name))

    if len(plugins == 1):
        log.info("Plugin {0} identified as target plugin.".format(plugins))
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


def get_plugins():
    """ Get a list of available plugins.

    Gets the basename of each folder name in the plugins directory
    and returns the list as the list of plugins.
    """
    plugin_dir = os.environ['COPILOT_PLUGINS_DIRECTORY'] + "/plugins/"
    # Get all folder names in plugins directory
    # remove the directory cruft to make them plugin names
    plugins = [os.path.basename(x[0]) for x in os.walk(plugin_dir)
               if os.path.basename(x[0]) != "plugins"]
    log.debug("Plugins found: {0}".format(plugins))
    return plugins

def is_plugin(name):
    """ Check if a string is the name of a plugin.

    Args:
        name (str): A possible plugin name
    """
    log.debug("Checking if plugin {0} exists".format(name))
    plugins = get_plugins()
    if name in plugins:
        log.debug("plugin {0} exists.".format(name))
        return True
    else:
        log.debug("plugin {0} does not exist.".format(name))
        return False


def is_service(service):
    """ Checks if a string is the name of a plugin service.

    Examines the current services being managed by SupervisorCTL
    and checks if the string passed matches the name of any of
    those services.

    Args:
        service (str): A possible service name.
    """
    log.debug("Checking if service exists.")
    services = []
    for line in subprocess.check_output(['supervisorctl', 'status']).split('\n'):
        log.debug("Service line received: {0}".format(line))
        match_name = re.search("^([^\s]*)\s*([A-Z]*)", line)
        if match_name and match_name.group(1) != "":
            services.append(match_name.group(1))
    if service in services:
        log.debug("Service Exists")
        return True
    else:
        log.debug("Service does not exist.")
        return False
