from pluginbase import PluginBase
import os


# stat logging
import logging
log = logging.getLogger(__name__)

plugin_base = PluginBase(package='copilot.plugins',
                         searchpath=[get_path("/home/www/co-pilot/copilot/plugins")])

class Plugin(object):
    def __init__(self, name):
        # Each plugin has a name
        self.name = name

        # and a source which loads the plugins from the "plugins/PLUGIN_NAME"
        # folder.
        self.source = plugin_base.make_plugin_source(
            searchpath=[get_path('./plugins/{0}'.format(self.name))],
            identifier=self.name)

        # Here we list all the plugins the source knows about, load them
        # and the use the "setup" function provided by the plugin to
        # initialize the plugin.
        for plugin_name in self.source.list_plugins():
            plugin = self.source.load_plugin(plugin_name)
            plugin.setup(self)

    def get_config_writer(self):
        config = plugin_source.load_plugin('config')
        config_writer = config.ConfigWriter()
        return config_writer

def get_plugins():
    plugin_dir = "/home/www/co-pilot/copilot/plugins"
    # Get all folder names in plugins and remove the directory cruft to make them plugin names
    return [x[0][2:] for x in os.walk(directory) if x[0] != "."]

def is_plugin(name):
    plugins = get_plugins
    if name in plugins:
        return True
    else:
        return False
