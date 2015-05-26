from functools import partial
import os
import subprocess
import re

# stat logging
import logging
log = logging.getLogger(__name__)

# For easier usage calculate the path relative to here.
# See: https://github.com/mitsuhiko/pluginbase/blob/master/example/example.py
here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)

def get_plugins():
    plugin_dir = "/home/www/copilot/copilot/plugins"
    # Get all folder names in plugins and remove the directory cruft to make them plugin names
    plugins = [os.path.basename(x[0]) for x in os.walk(plugin_dir) if os.path.basename(x[0]) != "plugins"]
    log.debug("Plugins found: {0}".format(plugins))
    return plugins

def is_plugin(name):
    plugins = get_plugins()
    if name in plugins:
        return True
    else:
        return False


def is_service(service):
    services = []
    for line in subprocess.check_output(['supervisorctl', 'status']).split('\n'):
        log.debug("Service line received: {0}".format(line))
        match_name = re.search("^([^\s]*)\s*([A-Z]*)", line)
        if match_name and match_name.group(1) != "":
            services.append(match_name.group(1))
    if service in services:
        return True
    else:
        return False
