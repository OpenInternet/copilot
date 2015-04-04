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
    """Get current status items. """
    print("get_status_items is currently not implemented")
    status_items = [{"icon":"wifi", "value":"[AP NAME HERE]", "status":"on"},
                    {"icon":"gears", "value":"Configure", "status":"null"},
                    {"icon":"profile", "value":"[PROFILE NAME]","status":"off"},
                    {"icon":"load", "value":"Load Profile","status":"load"}]
    return status_items

