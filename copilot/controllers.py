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

