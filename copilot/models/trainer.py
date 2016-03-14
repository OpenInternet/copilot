import string
from flask.ext.login import LoginManager
from copilot import app
from copilot import bcrypt, db
from flask.ext.login import UserMixin
from copilot.models.config import get_config_writer

#stat logging
import logging
log = logging.getLogger(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "login"

@login_manager.user_loader
def load_user(userid):
    """ Load the user object using the login manager"""
    _user = get_trainer()
    if not _user:
        log.info("No trainer object found. Assuming a new user.")
    return _user

def get_trainer():
    """ Get the trainer user object.

    CoPilot only allows for a single user. This function will return
    the first Trainer object in the database.
    """
    _trainer = Trainer.query.first()
    if not _trainer:
        log.info("No trainer found.")
    return _trainer

def get_ap_status():
    """ Get the state and name of CoPilot's access point.

    Checks for the current access point name and if it is
    set returns the name and an indicator that the access
    point is currently working.

    The try/except stanza that sets the status of the current_ap
    should actually evaluate if CoPilot is providing an access
    point instead of simply looking for if the AP name is set
    in the trainer and showing a "on" state if it does not raise
    an exception.
    """
    trainer = get_trainer()
    ap = {}
    current_ap = False
    try:
        current_ap = trainer.ap_name
    except:
        log.warn("FIX THIS SOON (function get_ap_status)")
    if current_ap:
        ap['status'] = "on"
        ap['value'] = current_ap
    else:
        ap['status'] = "off"
        ap['value'] = "NONE"
    return ap

class Base(db.Model):
    """ The base database model for CoPilot"""

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

class Trainer(Base, UserMixin):
    """ The trainer database model

    This is a single user database model because CoPilot is not intended to
    be used with multiple trainers sharing the same device with varying levels
    of access.
    """

    __tablename__ = 'trainer'

    #DataBase Values
    # Ensure Solo account
    _solo  = db.Column(db.Boolean,  default=True, nullable=False)
    # AP Name
    _ap_name   = db.Column(db.String(128),  nullable=False)
    # AP password
    _ap_password = db.Column(db.String(192),  nullable=False)
    # Trainer password
    _password = db.Column(db.String(192),  nullable=False)
    _current = db.Column(db.String(192),  nullable=True)

    def __init__(self, trainer_pass, ap_name="copilot", ap_password="copilot_pass"):
        log.debug("Creating new trainer object.")
        log.debug("Trainer AP: {0}".format(ap_name))
        self.password = trainer_pass
        self.solo = True
        self.current = False
        self.ap_name = ap_name
        self.ap_password = ap_password
        self.ap_config = get_config_writer("create_ap")
        log.debug(dir(self.ap_config))
        self.ap_config.add_rule(self.ap_name, self.ap_password)

    @property
    def solo(self):
        return self._solo

    @solo.setter
    def solo(self, val=True):
        self._solo = True

    @property
    def ap_name(self):
        return self._ap_name

    @ap_name.setter
    def ap_name(self, plaintext):
        self._ap_name = plaintext

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        """Admin password setter

        Passwords are hashed using bcrypt and then saved.
        """
        self._password = bcrypt.generate_password_hash(plaintext)

    @property
    def ap_password(self):
        return self._ap_password

    @ap_password.setter
    def ap_password(self, plaintext):
        """Access Point Password Setter (plaintext)

        This needs to be written in plain-text so that it can be passed
        to create_ap when starting the access point.
        """
        self._ap_password = plaintext


    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, plaintext):
        self._current = plaintext

    def is_correct_password(self, plaintext):
        """Compare the password provided with the saved password.

        Compares a hash of the string provided with the hash of the
        current saved password.

        Args:
            plaintext (str): a password to check.
        """
        return bcrypt.check_password_hash(self._password, plaintext)

    def __repr__(self):
        return '<Ap Name %r Solo %r>' % (self.ap_name, self.solo)
