---
layout: post
title:  "Plugin Guide"
categories: developer
---

<div class="plugin-head">

![Co-Pilot Plugin Logo](https://raw.github.com/wiki/openinternet/co-pilot/images/plugins_logo.png)

</div>

### What is a Plugin?

All the core functionality of Co-Pilot (censorship and networking) is provided plugins that use the Co-Pilot Plugin Interface. This plugin system allows developers to easily add new censorship, surveillance, or networking functionality to Co-Pilot without having in-depth knowledge of how Co-Pilot's back-end works or having had experience working with its underlying code-base.

### Why Plugins?

The Co-Pilot team [faced continuous requests](https://github.com/OpenInternet/co-pilot/issues/25) from developers during [Co-Pilots initial research and development](https://github.com/OpenInternet/co-pilot/wiki/Research-&-Development) to add different types of functionality to Co-Pilot. Just as the ability to create tailored censorship profiles was critical to the long-term adoption and use of Co-Pilot for trainers, developers saw the ability for outsiders to extend the Co-Pilot software as vital to its long-term viability as a core digital security training tool. In response to this Co-Pilot was re-engineered to include a plugin system at its core.

### What makes up a plugin?

Plugins are made up of 2 configuration files, one installation script, on start-up script, and a small script to allow the plugin to write, and save, its own configuration files. An example plugin can be found in [the docs repository](https://github.com/OpenInternet/co-pilot/tree/master/docs/example_plugin).

#### Required package files

* plugin.conf

The configuration file for the plugin. **REQUIRED**

* supervisor.conf

The supervisor program configuration that you want added to the final supervisor.conf

* config.py

The python file that contains the ```ConfigWriter``` object used to write and validate configs. **REQUIRED**

* install

The executable script that is used to install and configure the package.

* start

The executable script that is used to start and clean up after the package. **REQUIRED**

* \__init\__.py

An empty file that allows co-pilot to use this folder as a package. **REQUIRED**

### How do I write a plugin?

In order to support developers using the plugin system the Co-Pilot team also created an [example plugin](https://github.com/OpenInternet/co-pilot/tree/master/docs/example_plugin) and a [plugin management menu](https://github.com/OpenInternet/co-pilot/wiki/Plugin-Guide#restarting-a-plugin-using-the-copilot-user-interface) that allows developers to monitor and restart a plugins from the Co-Pilot web interface.

#### Naming your plugin

A plugin must have a unique name. A plugin name should also be descriptive of its functionality so that trainers and other developers can identify the service to restart when profiles are behaving incorrectly.

#### Adding the required files for your plugin

* Fork the [Co-Pilot repository.](https://github.com/OpenInternet/co-pilot)
* Add a folder in the [plugins directory](https://github.com/OpenInternet/co-pilot/tree/master/copilot/plugins) named similarly to the name of your plugin.
* Add the following blank files to this repository.
  * package.conf
  * supervisor.conf
  * config.py
  * install
  * start
  * \__init\__.py

#### Creating a package config file

The ```package.conf``` file is a configuration file that Co-Pilot uses to load the package and properly integrate its functionality into the Co-Pilot user interface.

##### The info header

A configuration file must start with an *info header* that looks like the following:

```
[info]
```

##### Valid Values

**name:** The name of your plugin.

**config_file:** The name of the configuration file that Co-Pilot should write to.

**target:** The target(s) you would like trainers to be able to choose from.

**actions:**The action(s) you would like trainers to be able to choose from.

**directory:** The directory that co-pilot should store your config files in

##### Required Values

The following values are required.

* name
* config_file
* directory

##### Example Config

```
[info]
name = my_config
config_file = my_plugin.conf
target = "website"
actions = fake
          block
directory = /tmp/copilot/
```


#### Creating an install script


#### Creating a supervisor script

Co-Pilot uses [Supervisor](http://supervisord.org) to control starting, stopping, and restarting its plugins. If you create a file named ```supervisor.conf``` in your plugin directory Co-Pilot will append it to the existing supervisor.conf. This file should be a [valid supervisor program configuration section](http://supervisord.org/configuration.html#program-x-section-settings).

##### Example Supervisor Script

```
[program:myplugin]
command = /home/www/copilot/copilot/plugins/myplugin/start
directory = /home/www/copilot/copilot/plugins/myplugin
user = root
autostart=true
autorestart=true
```

#### Creating a start script


```
##!/bin/bash

## Setting up the config file for my plugin
readonly config_file="/tmp/copilot/my_plugin.conf"

## In this simple case we just have to specify that we are using a config file when one exists.
## You can look at the existing plugins for how they read configuration file values.
start_create_ap() {
    if [[ -e $(config_file) ]]; then
        echo "Starting with a custom config."
        /usr/bin/my_plugin --config $(config_file)
    else
        echo "Starting with the default config."
        /usr/bin/my_plugin
    fi
}

## If you have any cleanup of process' that may need to be reset, killed, etc. you will want to clean them up in a trap function
cleanup() {
    killall my_plugin_children
    exit 0
}

## In this case, this just calls one program
## More complex programs may need multiple process' run to set them up.
main() {
    start_create_ap
}

## The trap function for killing all process' missed by supervisor gets set.
trap 'cleanup' EXIT

## The main function that runs your plugin is called.
main

```

#### Creating a configuration file writer

Your plugin will have different configuration file needs than any other program. To handle this we have created a [Python based "configuration writer" class](https://github.com/OpenInternet/co-pilot/blob/master/copilot/models/config.py#L140-L204) that can be customized to write all manner of configuration files. [You can see an example of a customized config writer in the DNS plugin](https://github.com/OpenInternet/co-pilot/blob/master/copilot/plugins/dns/config.py)

##### Minimal Configuration Example

Below is the most minimal example of a config writer plugin. This plugin will take rules that are passed to it and write them directly to the file specified in its profile without modifying them.

```
from copilot.models.config import Config

class ConfigWriter(Config):
    def __init__(self):
        super(ConfigWriter, self).__init__()
        self.config_type = "MY_PLUGIN_NAME"
```

##### The structure and API for ConfigWriter

###### add_rule

This function takes a single rule, checks if that rule is valid, transforms and formats the rule, and adds that rule to the self._rules list in a way that can be processed by the writer.

####### Args:
* rule: A list containing the action, target, and sub-target of a rule as three strings.
```
action, target, sub_target = rule[0], rule[1], rule[2]
```

####### Example
[This example is pulled directly from the DNS plugin.](https://github.com/OpenInternet/co-pilot/blob/master/copilot/plugins/dns/config.py#L18-L36)

```
def add_rule(self, rule):
    action, target, sub = rule[0], rule[1], rule[2]
    _rule, _domain, _address = "", "", ""
    log.debug("Adding rule {0} {1} {2}".format(action, target, sub))
    try:
        _domain = self.get_dns(sub)
    except ValueError as err:
        log.warning("Could not add rule. Invalid Target.")
        raise ValueError(err)
    if action == "block":
        log.debug("Found a blocking role. Setting address to localhost (127.0.0.1).")
        _address = "127.0.0.1"
    elif action == "redirect":
        log.debug("Found a redirection role. Setting address to default AP address (192.168.12.1).")
        _address = "192.168.12.1"
    _rule = "{0} = {1}\n".format(_domain, _address)
    self._rules.append(_rule)
```

###### write
Opens, and clears, the specified config file and writes the header and then all of the rules for this config. You will only want to modify this if you wish to change the fundamental way that your configuration file writes configs.

####### Example
In this example the write function has been re-written to only write rules, and not write the header text to the config file.
```
def write(self):
        self.prepare()
        log.debug("Opening config file {0} for writing.".format(self.config_file))
        with open(self.config_file, 'w+') as config_file:
            for rule in self._rules:
                self.write_rule(config_file, rule)
```

###### write_rule(self, config_file, rule):
desc
####### Args:
* config_file:
A file handler for a config file to write to.
* rule:
A string that should be written to the file.

####### Example
An example of an alternative write rule function that shows how it can be modified to fit different use cases.
```
```


###### write_header(self, config_file):
description

####### Args:

* config_file:
A file handler for a config file to write to.

####### Example

An example of an alternative write header function that shows how it can be modified to fit different use cases.

```
```


##### How data is passed to a Plugin




#### Adding a watchdog rule

Currently adding a watchdog rule is the only place where you will need to edit an existing piece of code. This will be streamlined in the future.

To edit this you will first need to open the [watchdog script](https://github.com/OpenInternet/co-pilot/blob/master/bin/watch_config).

You will then need to add your config file to the configs that it watches. You do this by adding the following line into the [main configuration block.](https://github.com/OpenInternet/co-pilot/blob/d200e33c896593314c751301faadd24e6015a8f0/bin/watch_config#L39-L45)


```
config_handle.add_config("MYCONFFILE", "MYSUPERVISORNAME")
```

Replace ```MYSUPERVISORNAME``` with the name you gave your program in your ```supervisor.conf``` file.

Replace ```MYCONFFILE``` with the ```config_file``` value from your configuration file.

### How do I install a plugin?

* Fork the co-pilot github repository
* Add your plugin to the [plugins folder.](https://github.com/OpenInternet/co-pilot/tree/master/copilot/plugins)

```
co-pilot/copilot/plugins/[PLUGIN_NAME]
```

* Follow the [Installation Guide](https://github.com/OpenInternet/co-pilot/wiki/Installing-Co-Pilot) replacing the URL of the core copilot repository with the URL of your repository.


### How do I troubleshoot my plugin?

#### Restarting a plugin using the copilot user interface

In the copilot user interface, in the info menu you can restart a plugin by clicking on the circular arrow icon next to your plugins name.

![plugins page](https://raw.github.com/wiki/openinternet/co-pilot/images/plugins.png)

#### Checking your plugins logs

Error log location.
```
/var/log/supervisor/PLUGIN_NAME-stderr---supervisor-*
```

Standard output log location.
```
/var/log/supervisor/PLUGIN_NAME-stdout---supervisor-*
```
