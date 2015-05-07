from copilot import app
from flask.ext.login import LoginManager
from copilot.models.trainer import get_ap_status
from copilot.models.profile import get_profile_status

#stat logging
import logging
log = logging.getLogger(__name__)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "login"



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
