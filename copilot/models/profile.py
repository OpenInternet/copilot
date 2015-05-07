import string
from copilot import bcrypt, db
from flask.ext.login import UserMixin
import csv
import os
import uuid
from urlparse import urlparse
import subprocess
from copilot.models.config import get_config_dir, get_config_file, get_valid_targets, get_valid_actions
from config import DNSConfig

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

class Profile:
    def __init__(self, name, description=None, rules={}):
        self.rules = []
        self._profile_dir = get_config_dir("profiles")
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
        if not os.path.exists(self._profile_dir):
            os.makedirs(self._profile_dir)
        profile_file = (self._profile_dir + self.name)
        #Empty the file
        open(profile_file, 'w').close()
        #Save rules to file
        for rule in self.rules:
            rule.save(profile_file)
        log.info("Profile {0} saved".format(self.name))

    def exist(self):
        profile_file = (self._profile_dir + self.name)
        if os.path.isfile(profile_file):
            log.info(" profile {0} exists".format(self.name))
            return True
        else:
            log.info(" profile {0} does NOT exists".format(self.name))

    def load(self):
        profile_file = (self._profile_dir + self.name)
        with open(profile_file, 'r') as csvfile:
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
