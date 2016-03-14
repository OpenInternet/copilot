from functools import partial
import os
import subprocess
import re

# stat logging
import logging
log = logging.getLogger(__name__)


def get_plugins():
    """ Get a list of available plugins.

    Gets the basename of each folder name in the plugins directory
    and returns the list as the list of plugins.
    """
    plugin_dir = os.environ['COPILOT_PLUGINS_DIRECTORY'] + "/plugins/"
    # Get all folder names in plugins directory
    # remove the directory cruft to make them plugin names
    plugins = []
    for item in os.listdir(plugin_dir):
        if os.path.isfile(os.path.join(plugin_dir, item, "config.py")):
            plugins.append(item)
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
