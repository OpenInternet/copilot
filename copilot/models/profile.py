import string
from copilot import bcrypt, db
from flask.ext.login import UserMixin
import csv
import os
import uuid
import subprocess
from copilot.models.config import get_config_dir, get_config_file, get_valid_targets, get_valid_actions, get_config_writer, ProfileConfig
from copilot.models.trainer import get_trainer
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
    profiles = []
    for _dir in _profile_dirs:
        if os.path.isdir(_dir):
            for _prof in os.listdir(_dir):
                p_path = os.path.join(_dir, _prof)
                if os.path.isfile(p_path):
                    _test = ProfileConfig(p_path)
                    if _test.valid():
                        profiles.append(_prof)
    return profiles


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
        log.debug("adding rule {0} {1} {2}".format(rule['action'], rule['target'], rule['sub_target']))
        config_obj = get_config_writer(rule['target'])
        try:
            config_obj.add_rule([rule['action'], rule['target'], rule['sub_target']])
        except ValueError as _err:
            log.error("Error Encountered in add_rule()")
            log.info("Rule is NOT valid")
            raise ValueError(_err) #TODO add real error correction here
        self.rules.append([rule['action'], rule['target'], rule['sub_target']])

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
                _prof.set_rule(rule)
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

        configs = {}
        log.info("looking for config files that need to be written.")
        targets = get_package_configs("target")
        for r in self.rules:
            _action = r[0]
            _tar = r[1]
            _sub = r[2]
            if _tar not in _configs:
                log.debug("Creating a {0} config".format(_tar))
                configs[r.target] = get_config_writer(_tar)
                log.debug("Adding a rule ({0} {1}) to {2} config.".format(_tar, _action, _sub))
                configs[r.target].add_rule(_tar, _action, _sub)
            else:
                log.debug("Adding a rule ({0} {1}) to {2} config.".format(_tar, _action, _sub))
                configs[r.target].add_rule(_tar, _action, _sub)
        for c in configs:
            log.debug("Writing {0} config.".format(c))
            configs[c].write()
