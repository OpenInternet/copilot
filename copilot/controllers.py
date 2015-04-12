from copilot import app
from flask.ext.login import LoginManager
from copilot.models import Trainer

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "login"

@login_manager.user_loader
def load_user(userid):
    return get_trainer()

def get_trainer():
    """Only allow one trainer account. """
    return Trainer.query.first()


def get_status_items():
    """Get current status items.
    icon: the ID of the svg to use.
    value: The text to put under the icon
    status: [off/on/error] The color of the icon background to use (off=grey, on=green, error=orange)
    """
    print("TODO: get_status_items is currently not implemented")
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

def get_profile_status():
    trainer = get_trainer()
    profile = {}
    current_profile = trainer.current
    if current_profile:
        profile['status'] = "on"
        profile['value'] = current_profile
    else:
        profile['status'] = "off"
        profile['value'] = "NONE"
    return profile

def get_ap_status():
    trainer = get_trainer()
    ap = {}
    current_ap = trainer.ap_name
    if current_ap:
        ap['status'] = "on"
        ap['value'] = current_ap
    else:
        ap['status'] = "off"
        ap['value'] = "NONE"
    return ap
