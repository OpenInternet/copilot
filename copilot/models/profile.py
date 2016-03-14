from copilot import db
from flask.ext.login import UserMixin
import os
from copilot.models.config import get_config_dir, get_config_writer, ProfileConfig, ProfileWriter, get_plugin_from_rules
from copilot.models.trainer import get_trainer
from copilot.utils.file_sys import get_usb_dirs
from werkzeug import secure_filename

#stat logging
import logging
log = logging.getLogger(__name__)

def get_profile_status():
    """ Gives the status and name of the currenty running profile.

    This function provides a status dict containing the name of the
    current profile (if any), and if that profile is enabled. There
    is currently no way to disable the currently running profile
    without creating and running a blank profile. As such, this
    funtion retuns disabled profiles only when there is no current
    trainer.
    """
    trainer = get_trainer()
    profile = {}
    current_profile = False
    try:
        current_profile = trainer.current
        log.debug("current profile found: {0}".format(current_profile))
    except:
        log.debug("No current trainer found. Returning broken profile.")
        log.warn("FIX THIS SOON: bare exception (function get_profile_status)")
    if current_profile:
        if current_profile == "0":
            current_profile = "No Active Profile"
        profile['status'] = "on"
        profile['value'] = current_profile
    else:
        profile['status'] = "off"
        profile['value'] = "NONE"
    return profile

def get_all_profiles():
    """ Get a list of all profiles on CoPilot"""
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
    """ A CoPilot profile.

    A profile is a set of rules (The combination of a target and
    an action) that are to be used together. For example a training profile
    may contain one rule to "Block HTTPS" traffic and another to "Block the
    URL www.google.com" so that trainee's can not use any HTTPS websites
    and cannot use google.com even if it is not using HTTPS.
    """

    def __init__(self, name, description="A co-pilot profile", rules={}):
        self.rules = []
        self.name = name
        self.profile_dir = "profiles"
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
        """ Set the profile's save directory

        Set the profiles save directory based upon the config type

        Args:
           plaintext (str): The configuration file type of this profile.
                See models/config.py get_config_dir() for available types.
        """
        try:
            _dir = get_config_dir(plaintext)
            self._profile_dir = _dir
            log.debug("profile directory set to {0}".format(self._profile_dir))
            try:
                log.debug("Profile name is {0}".format(secure_filename(self.name)))
                self.profile_file = os.path.join(self._profile_dir, secure_filename(self.name))
            except AttributeError as ee:
                log.debug("cannot set profile_file as {0} is not initialized yet.".format(plaintext))
                log.error("Error encountered {0}".format(ee))
                raise ValueError("{0}".format(ee))
        except ValueError:
            raise ValueError("\"{0}\" is not a valid co-pilot directory. It cannot be set.".format(plaintext))

    def add_rule(self, ruleset):
        """ Add a rule to the Profile object


        Args:
        ruleset (list|dict): a single set containing an  action, target, and sub_target.
        """
        # Rapid prototyping means that I just want the rule, I don't care how it is formatted.
        if isinstance(ruleset, dict):
            rule = ruleset
        elif isinstance(ruleset ,list):
            rule = {"action":ruleset[0],
                    "target":ruleset[1],
                    "sub_target":ruleset[2]}
            # Rules without sub-targets need a default to ignore
        log.debug("sub_target is |{0}|".format(rule['sub_target']))
        if rule['sub_target'] == "":
            log.debug("sub_target is an empty string")
            rule['sub_target'] = "SUB_TARGET_NOT_GIVEN"
        log.debug("adding rule {0} {1} {2}".format(rule['action'], rule['target'], rule['sub_target']))
        plugin_name = get_plugin_from_rules(rule.get('action',""), rule.get('target',""))
        config_obj = get_config_writer(plugin_name)
        try:
            config_obj.add_rule([rule['action'], rule['target'], rule['sub_target']])
        except ValueError as _err:
            log.error("Error Encountered in add_rule()")
            log.info("Rule is NOT valid")
            raise ValueError(_err) #TODO add real error correction here
        self.rules.append([rule['action'], rule['target'], rule['sub_target']])

    def save(self):
        """ Save the profile as a flat file in its profile directory."""
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
        """Checks if the profile file already exists."""
        if os.path.isfile(self.profile_file):
            log.info(" profile {0} exists".format(self.name))
            return True
        else:
            log.info(" profile {0} does NOT exists".format(self.name))
            return False

    def refresh(self):
        """Reload all profile values from its file.

        NOTE: This method does not check the currently set profile directory
        to re-create the path to the profile file. If you change a profiles
        directory you must also refresh the profile_file property for this
        function to refresh from the new location.
        """
        log.info("Refreshing profile from file.")
        config = ProfileConfig(self.profile_file)
        if not config.valid():
            raise ValueError("Config file is not valid. Cannot reload config")
        log.debug("Current name: {0}".format(self.name))
        self.name = config.data["info"]["name"][0]
        log.debug("Set profile name to {0}".format(self.name))
        log.debug("Current profile file: {0}".format(self.profile_file))
        self.profile_file = os.path.join(self.profile_dir, secure_filename(self.name))
        log.debug("Set profile file to {0}".format(self.profile_file))
        log.debug("Current description: {0}".format(self.description))
        if "description" in config.data["info"]:
            self.description = config.data["info"]["description"][0]
        log.debug("Set description to {0}".format(self.description))
        log.debug("Current rules: {0}".format(self.rules))
        log.debug("clearing all existing rules")
        self.rules = []
        _rules = config.get_rules()
        for r in _rules:
            self.add_rule(r)
        log.debug("Set rules to {0}".format(self.rules))

    def load(self):
        """Load a profile from a file.

        NOTE: This method does not check the currently set profile directory
        to re-create the path to the profile file. If you change a profiles
        directory you must also refresh the profile_file property for this
        function to load from the new location.
        """
        log.info("Loading profile.")
        log.debug("Using profile at {0}".format(self.profile_file))
        config = ProfileConfig(self.profile_file)
        if not config.valid():
            raise ValueError("Config file is not valid. Cannot load config")
        self.name = config.data["info"]["name"][0]
        log.debug("Set profile name to {0}".format(self.name))
        self.profile_file = os.path.join(self.profile_dir, secure_filename(self.name))
        log.debug("Set profile file to {0}".format(self.profile_file))
        if "description" in config.data["info"]:
            self.description = config.data["info"]["description"][0]
        log.debug("Set description to {0}".format(self.description))
        _rules = config.get_rules()
        for r in _rules:
            self.add_rule(r)
        log.debug("Set rules to {0}".format(self.rules))

    def apply_config(self):
        """Apply and start running the current profile.

        This method both sets the current profile as the "current"
        profile and writes the approptiate configuration files for
        the rules contained within the profile.
        """
        log.info("Applying profile {0}".format(self.name))
        trainer = get_trainer() #Save as current profile for trainer.
        trainer.current = self.name
        db.session.commit()

        configs = {}
        log.info("looking for config files that need to be written.")
        for rule in self.rules:
            _action = rule[0]
            _target = rule[1]
            _sub_target = rule[2]
            plugin_name = get_plugin_from_rules(_action, _target)
            configs.setdefault(plugin_name, get_config_writer(plugin_name))
            log.debug("Adding a rule ({0} {1}) to {2} config.".format(_action, _target, _sub_target))
            configs[plugin_name].add_rule([_action, _target, _sub_target])
        for config, conf_writer in configs.items():
            log.debug("Writing {0} config.".format(config))
            conf_writer.write()
