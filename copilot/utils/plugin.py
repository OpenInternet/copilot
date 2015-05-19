from pluginbase import PluginBase
from functools import partial
import os

# stat logging
import logging
log = logging.getLogger(__name__)

# For easier usage calculate the path relative to here.
# See: https://github.com/mitsuhiko/pluginbase/blob/master/example/example.py
here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)

plugin_base = PluginBase(package='copilot.plugins')

class Plugin(object):
    def __init__(self, name):
        # Each plugin has a name
        self.name = name

        # and a source which loads the plugins from the "plugins/PLUGIN_NAME"
        # folder.
        self.source = plugin_base.make_plugin_source(
            searchpath=[get_path('/home/www/copilot/copilot/plugins/{0}'.format(self.name))],
            identifier=self.name)
        log.debug(self.source.searchpath)
        # Here we list all the plugins the source knows about, load them
        # and the use the "setup" function provided by the plugin to
        # initialize the plugin.
        for plugin_name in self.source.list_plugins():
            log.debug("Loading sub-plugin {0} from plugin: {1}".format(plugin_name, self.name))

    def get_config_writer(self):
        return self.source.load_plugin("config")

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
