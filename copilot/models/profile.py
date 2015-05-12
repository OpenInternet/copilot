import string
from copilot import bcrypt, db
from flask.ext.login import UserMixin
import csv
import os
import uuid
import subprocess
from copilot.models.config import get_config_dir, get_config_file, get_valid_targets, get_valid_actions
from copilot.models.trainer import get_trainer
from config import DNSConfig
from copilot.utils.file_sys import get_usb_dirs
from werkzeug import secure_filename

#stat logging
import logging
log = logging.getLogger(__name__)

def get_profile_status():
    trainer = get_trainer()
    profile = {}
    current_profile = False
    try:
        current_profile = trainer.current
    except:
        log.warn("FIX THIS SOON (function get_profile_status)")
    if current_profile:
        profile['status'] = "on"
        profile['value'] = current_profile
    else:
        profile['status'] = "off"
        profile['value'] = "NONE"
    return profile

def get_all_profiles():
    _profile_dirs = get_usb_dirs()
    _profile_dirs.append(get_config_dir("profiles"))
    possible_profiles = []
    for _dir in _profile_dirs:
        if os.path.isdir(_profile_dir):
            for _prof in listdir(_profile_dir):
                if isfile(join(_profile_dir, _prof)):
                    possible_profiles.append(_prof)
    profiles = []
    for pp in possible_profiles:



class Profile(object):
    def __init__(self, name, description="A co-pilot profile", rules={}):
        self.rules = []
        self.profile_dir = "profiles"
        self.name = name
        self.profile_file = os.path.join(self.profile_dir, secure_filename(self.name))
        self.description = description
        if rules:
            try:
                for rule in rules:
                    self.add_rule(rule)
            except ValueError as _err: #TODO add real error correction here
                raise _err
    @property
    def profile_dir(self):
        return self._profile_dir

    @profile_dir.setter
    def profile_dir(self, plaintext):
        try:
            _dir = get_config_dir(plaintext)
            self._profile_dir = _dir
        except ValueError:
            raise ValueError("\"{0}\" is not a valid co-pilot directory. It cannot be set.".format(plaintext))

    def add_rule(self, rule):
        log.debug("adding rule {0} {1} {2}".format(rule.action, rule.target, rule.sub_target))
        try:
            rule_obj = Rule(rule.target, rule.action, rule.sub_target)
        except ValueError as _err:
            log.error("Error Encountered in add_rule()")
            raise ValueError(_err) #TODO add real error correction here
        if rule_obj.is_valid():
            log.info("Rule is valid")
            self.rules.append(rule_obj)
        else:
            log.info("Rule is NOT valid")

    def save(self):
        log.info("Saving profile {0} to {1}".format(self.name, self.profile_file))
        if not os.path.exists(self.profile_dir):
            os.makedirs(self.profile_dir)
        with open(self.profile_file, "w+") as config_file:
            _prof = ProfileWriter()
            _prof.add_section("info")
            _prof.set("info", "name", self.name)
            _prof.set("info", "description", self.description)
            for rule in self.rules:
                _prof.set_rule(rule.action, rule.target, rule.sub_target)
            _prof.write(config_file)
        log.info("Profile {0} saved".format(self.name))

    def exist(self):
        if os.path.isfile(self.profile_file):
            log.info(" profile {0} exists".format(self.name))
            return True
        else:
            log.info(" profile {0} does NOT exists".format(self.name))
            return False

    def refresh(self):
        """
        Reload all profile values from its file.

        NOTE: Does not change the profile directory.
        """
        log.info("Refreshing profile from file.")
        config = ProfileConfig(self.profile_file)
        if not config.valid():
            raise ValueError("Config file is not valid. Cannot reload config")
        log.debug("Current name: {0}".format(self.name))
        self.name = config["info"]["name"][0]
        log.debug("Set profile name to {0}".format(self.name))
        log.debug("Current profile file: {0}".format(self.profile_file))
        self.profile_file = os.path.join(self.profile_dir, secure_filename(self.name))
        log.debug("Set profile file to {0}".format(self.profile_file))
        log.debug("Current description: {0}".format(self.description))
        if "description" in config["info"]:
            self.description = config["info"]["description"][0]
        log.debug("Set description to {0}".format(self.description))
        log.debug("Current rules: {0}".format(self.rules))
        log.debug("clearing all existing rules")
        self.rules = []
        _rules = config.get_rules()
        for r in _rules:
            self.add_rule(r)
        log.debug("Set rules to {0}".format(self.rules))

    def load(self):
        """
        Load a profile from a file.

        NOTE: Does not change the profile directory.
        """
        log.info("Loading profile.")
        config = ProfileConfig(self.profile_file)
        if not config.valid():
            raise ValueError("Config file is not valid. Cannot load config")
        self.name = config["info"]["name"][0]
        log.debug("Set profile name to {0}".format(self.name))
        self.profile_file = os.path.join(self.profile_dir, secure_filename(self.name))
        log.debug("Set profile file to {0}".format(self.profile_file))
        if "description" in config["info"]:
            self.description = config["info"]["description"][0]
        log.debug("Set description to {0}".format(self.description))
        _rules = config.get_rules()
        for r in _rules:
            self.add_rule(r)
        log.debug("Set rules to {0}".format(self.rules))

    def apply_config(self):
        log.info("Applying profile {0}".format(self.name))
        trainer = get_trainer() #Save as current profile for trainer.
        trainer.current = self.name
        db.session.commit()

        _configs = {}
        log.info("looking for config files that need to be written.")
        _targets = get_valid_targets()
        for r in self.rules:
            if r.target not in _configs:
                #TODO This needs to be replaced with some sort of config file that checks the proper config object to instantiate when a specific config type is passed.
                if r.target == "dns":
                    log.debug("Creating a {0} config".format("dnschef"))
                    _configs["dns"] = DNSConfig()
                    log.debug("Adding a rule ({0} {1}) to dnschef config.".format(r.action, r.sub_target))
                    _configs["dns"].add_rule(r.target, r.action, r.sub_target)
            else:
                if r.target == "dns":
                    log.debug("Adding a rule ({0} {1}) to dnschef config.".format(r.action, r.sub_target))
                    _configs["dns"].add_rule(r.target, r.action, r.sub_target)
        for c in _configs:
            log.debug("Writing {0} config.".format(c))
            _configs[c].write()

class Rule(object):

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

    def __repr__(self):
        return "{0} {1} {3}".format(self.action, self.target, self.sub_target)
