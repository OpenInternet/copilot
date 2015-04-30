import string
from copilot import bcrypt, db
from flask.ext.login import UserMixin
import csv
import os
import uuid
from urlparse import urlparse
import subprocess
from controllers import get_config_dir, get_config_file, get_valid_targets, get_valid_actions
from config import DNSConfig

#stat logging
import logging
log = logging.getLogger(__name__)

class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

class Trainer(Base, UserMixin):
    """ The trainer (SINGLE user) model"""

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

    def __init__(self, trainer_pass, ap_name="copilot", ap_password="copilot"):
        self.password = trainer_pass
        self.ap_name = ap_name
        self.ap_password = ap_password
        self.solo = True
        self.current = False

    @property
    def solo(self):
        return self._solo

    @solo.setter
    def solo(self, val=True):
        self._solo = True

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, plaintext):
        self._current = plaintext

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

    @property
    def ap_password(self):
        return self._ap_pass

    @password.setter
    def ap_password(self, plaintext):
        if (8 < len(str(plaintext)) <= 63 and
            all(char in string.printable for char in plaintext)):
            self._ap_password = plaintext
        else:
            print(plaintext)
            raise ValueError("Access Point passwords must be between 8 and 63 characters long and use only printable ASCII characters.")

    @property
    def ap_name(self):
        return self._ap_name

    @ap_name.setter
    def ap_name(self, name):
        if 0 < len(str(name)) <= 31:
            self._ap_name = name
        else:
            raise ValueError("Access Point names must be between 1 and 31 characters long.")

    def write_ap_config(self):
        #TODO Replace with config obj
        AP_CONFIG = get_config_file("create_ap")
        with open(AP_CONFIG, 'w') as config_file:
            config_file.write("wlan0 eth0 {0} {1}".format(self._ap_name, self._ap_password))

    def __repr__(self):
        return '<Ap Name %r Solo %r>' % (self.ap_name, self.solo)

class Profile:
    def __init__(self, name, description=None, rules={}):
        self.rules = []
        self.name = name
        self.description = description
        if rules:
            try:
                for rule in rules:
                    self.add_rule(rule)
            except ValueError as _err: #TODO add real error correction here
                raise _err

    def add_rule(self, rule):
        log.debug("adding rule {0} {1} {2}".format(rule.action, rule.target, rule.sub_target))
        try:
            _rule = Rule(rule.target, rule.action, rule.sub_target)
        except ValueError as _err:
            log.error("Error Encountered in add_rule()")
            raise ValueError(_err) #TODO add real error correction here
        if _rule.is_valid():
            log.info("Rule is valid")
            self.rules.append(_rule)
        else:
            log.info("Rule is NOT valid")

    def save(self):
        log.info("saving profile {0}".format(self.name))
        if not os.path.exists(PROFILE_DIR):
            os.makedirs(PROFILE_DIR)
        PROFILE_FILE = (PROFILE_DIR + self.name)
        #Empty the file
        open(PROFILE_FILE, 'w').close()
        #Save rules to file
        for rule in self.rules:
            rule.save(PROFILE_FILE)
        log.info("Profile {0} saved".format(self.name))

    def exist(self):
        PROFILE_FILE = (PROFILE_DIR + self.name)
        if os.path.isfile(PROFILE_FILE):
            log.info(" profile {0} exists".format(self.name))
            return True
        else:
            log.info(" profile {0} does NOT exists".format(self.name))

    def load(self):
        PROFILE_FILE = (PROFILE_DIR + self.name)
        with open(PROFILE_FILE, 'r') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in csv_reader:
                _rule=Rule(row[0], row[1], row[2])
                self.add_rule(_rule)

    def write_config(self, config_type):
        """Writes a config file.

        config (str): the type of config to write.
        """
        log.debug("writing config.")
        _config = create_config_obj(config_type)
        for r in self.rules:
            if r.action == config_type:
                _config.add_rule([r.target, r.sub_target])
        _config.write_config()

    def apply(self):
        _configs = []
        log.info("looking for config files that need to be written.")
        for r in self.rules():
            if r.action not in _configs:
                _configs.append(r.action)
        log.debug("{0} configs found:\n {1}".format(len(_configs), _configs))
        for c in _configs:
            self.write_config(c)


class Rule:

    def __init__(self, target, action, sub_target=""):
        self.valid_actions = get_valid_actions()
        self.valid_targets = get_valid_targets()
        self.errors = {}
        self.target = target
        self.action = action
        self.sub_target = sub_target
        self.uuid = uuid.uuid4()

    def init_validators(self):
        """TODO Make these actually validate address'"""
        self.valid_sub_targets = {
            url : True,
            dns : True}

    def save(self, save_file):
        with open(save_file, 'a') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=' ',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([self.target,  self.action, self.sub_target])

    def is_valid(self):
        if self.errors:
            return False
        else:
            return True

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, plaintext):
        try:
            value_to_set = self.valid_targets.index(string.lower(plaintext))
            self._target = plaintext
        except ValueError:
            raise ValueError("The target \"{0}\" is invalid.".format(plaintext))

    @property
    def sub_target(self):
        return self._sub_target

    @sub_target.setter
    def sub_target(self, plaintext):
        #If a target is not set then we cannot check the sub-target against it.
        if not self._target:
            raise ValueError("The sub-target \"{0}\" cannot be set without a valid target.".format(plaintext))
        print("TODO Validate sub-targets.")
        self._sub_target = plaintext

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, plaintext):
        try:
            value_to_set = self.valid_actions.index(string.lower(plaintext))
            self._action = plaintext
        except ValueError:
            raise ValueError("The action \"{0}\" is invalid.".format(plaintext))
