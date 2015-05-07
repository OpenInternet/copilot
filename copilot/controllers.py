from copilot import app
from flask.ext.login import LoginManager
from copilot.models.trainer import get_trainer, get_ap_status
from copilot.models.profile import get_profile_status


#stat logging
import logging
log = logging.getLogger(__name__)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "login"


CP_PACKAGES = {"dns":{"name": "dnschef",
                      "config_file": "dnschef.conf",
                      "target" : "dns",
                      "actions": ["block", "redirect"]},
               "ap":{"name": "create_ap",
                     "config_file": "ap.conf"}}

CP_ACTIONS = ['block']

def get_status_items():
    """Get current status items.
    icon: the ID of the svg to use.
    value: The text to put under the icon
    status: [off/on/error] The color of the icon background to use (off=grey, on=green, error=orange)
    """
    log.warn("TODO: get_status_items is currently not fully implemented")
    profile = get_profile_status()
    access_point = get_ap_status()
    status_items = [{"icon":"wifi",
                     "value":access_point['value'],
                     "status":access_point['status'],
                     "url":"config"},
                    {"icon":"config",
                     "value":"Configure",
                     "status":"off",
                     "url":"config"},
                    {"icon":"profile",
                     "value":profile['value'],
                     "status":profile['status'],
                     "url":"profile_current"},
                    {"icon":"load",
                     "value":"Load Profile",
                     "status":"off",
                     "url":"profile_load"}]
    return status_items

def get_config_dir(directory):
    directories = {"main","/tmp/copilot/",
                   "profiles", "/tmp/copilot/profiles"}
    if directory in directories:
        return directories[directory]
    else:
        raise ValueError("That config directory is not valid.")

def get_config_file(config):
    _copilot_dir = get_config_dir("main")
    configs = {}
    for item in CP_PACKAGES:
        if "config" in CP_PACKAGES[item]:
            configs[CP_PACKAGES[item]["name"]] = CP_PACKAGES[item]["config"]
    if config in configs:
        return configs[config]
    else:
        raise ValueError("That config file is not valid.")

def get_valid_targets():
    _targets = []
    for item in CP_PACKAGES:
        if "target" in CP_PACKAGES[item]:
            _targets.append([CP_PACKAGES[item]["target"]])
    return _targets

def get_valid_actions():
    return CP_ACTIONS
