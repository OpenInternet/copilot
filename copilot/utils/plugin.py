from functools import partial
import os

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
