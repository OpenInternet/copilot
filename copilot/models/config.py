import os
import string
from urlparse import urlparse

#stat logging
import logging
log = logging.getLogger(__name__)

"""
CP_PACKAGES = { "SERVICE NAME" : {
                   "name" : "SERVICE NAME",
                   "config_file": "CONFIG FILE NAME",
                   "target" : "TARGET NAME",
                   "actions": ["ACTION 001", "ACTION 002", "ACTION ETC"],
                   "directory":"DIRECTORY HEADING FROM CP_DIRS VAR"}
"""
#TODO Remove this variable and pull package configs from some sort of config file
CP_PACKAGES = {"dnschef":{"name": "dnschef",
                          "config_file": "dnschef.conf",
                          "target" : "dns",
                          "actions": ["block", "redirect"],
                          "directory":"main"},
               "create_ap":{"name": "create_ap",
                     "config_file": "ap.conf",
                     "directory":"main"}}

def get_config_dir(directory):
    directories = {"main" : "/tmp/copilot/",
           "profiles" : "/tmp/copilot/profiles"}
    if directory in directories:
        log.debug("Directory {0} found and being returned.".format(directory))
        return directories[directory]
    else:
        raise ValueError("That config directory is not valid.")

def get_config_file(config):
    """ return the path to a config file."""
    _copilot_dir = get_config_dir("main")
    if config in CP_PACKAGES:
        if "config_file" in CP_PACKAGES[config]:
            try:
                _directory = get_config_dir(CP_PACKAGES[config]["directory"])
                _path = os.path.join(_directory, CP_PACKAGES[config]["config_file"])
                log.debug("Returning config path {0}".format(_path))
                return _path
            except ValueError as err:
                log.error("Directory found in CP_PACKAGES under the {0} package was invalid.".format(config))
                raise ValueError(err)
    else:
        raise ValueError("That config file is not valid.")

def get_valid_actions():
    _valid_actions = ["block", "redirect"]
    return _valid_actions

def get_valid_targets():
    _targets = []
    for item in CP_PACKAGES:
        if "target" in CP_PACKAGES[item]:
            _targets.append(CP_PACKAGES[item]["target"])
    return _targets


class Config(object):

    def __init__(self):
        self._rules = []
        self.config_dir = "main"

    @property
    def config_type(self):
        return self._config_type

    @config_type.setter
    def config_type(self, config_type):
        try:
            config_file = get_config_file(config_type)
        except ValueError as err:
            log.error("An invalid config type was passed. Please check \"get_config_file\" in the models/config.py scripts for the valid types of config files.")
            raise ValueError(err)
        self._config_type = config_type
        self.config_file = config_file

    def check_file(self):
        if os.path.exists(self._config_file):
            return True
        else:
            return False

    def add_rule(self, rule):
        log.debug("adding rule {0}".format(rule))
        self._rules.append(rule)

    def write(self):
        self.prepare()
        log.debug("Opening config file {0} for writing.".format(self.config_file))
        with open(self.config_file, 'w+') as config_file:
            self.write_header(config_file)
            for rule in self._rules:
                self.write_rule(config_file, rule)

    def prepare(self):
        log.info("Creating the config directory if it does not exist.")
        _dir = get_config_dir(self.config_dir)
        if not os.path.exists(_dir):
            log.info("Creating the main config directory {0}.".format(_dir))
            os.makedirs(_dir)
        else:
            log.info("The config directory {0} exists and will not be created.".format(_dir))

    def write_rule(self, config_file, rule):
        log.debug("writing rule {0}".format(rule))
        config_file.write(rule)

    def write_header(self, config_file):
        log.debug("writing header info {0}".format(self.header))
        if self.header:
            log.debug("Found header. Writing to config file {0}".format(config_file))
            config_file.write(self.header)
        else:
            log.debug("No header found.")

class DNSConfig(Config):

    def __init__(self):
        super(DNSConfig, self).__init__()
        self.config_type = "dnschef"
        self.header = "[A]\n"

    def add_rule(self, target, action, sub):
        _rule = ""
        _domain = ""
        _address = ""
        try:
            _domain = self.get_dns(sub)
        except ValueError as err:
            log.warn("Could not add rule. Invalid Target.")
        if action == "block":
            log.debug("Found a blocking role. Setting address to localhost (127.0.0.1).")
            _address = "127.0.0.1"
        elif action == "redirect":
            log.debug("Found a redirection role. Setting address to default AP address (192.168.12.1).")
            _address = "192.168.12.1"
        _rule = "{0} = {1}\n".format(_domain, _address)
        self.rules.append(_rule)

    def get_dns(self, sub):
        tld = ["ac", "ad", "ae", "aero", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "arpa", "as", "asia", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "biz", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cat", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "com", "coop", "cr", "cs", "cu", "cv", "cw", "cx", "cy", "cz", "dd", "de", "dj", "dk", "dm", "do", "dz", "ec", "edu", "ee", "eg", "eh", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gov", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "info", "int", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jobs", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "local", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mil", "mk", "ml", "mm", "mn", "mo", "mobi", "mp", "mq", "mr", "ms", "mt", "mu", "museum", "mv", "mw", "mx", "my", "mz", "na", "name", "nato", "nc", "ne", "net", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "onion", "org", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "pro", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tel", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "travel", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "xxx", "ye", "yt", "yu", "za", "zm", "zr", "zw"]
        _sub = sub
        log.debug("sub target is {0}".format(_sub))
        if _sub == "":
            return None
        parsed = urlparse(_sub).path
        log.debug("parsed url is {0}".format(parsed))
        split_sub = string.split(parsed, ".")
        log.debug("split up sub target is {0}".format(split_sub))
        #TODO the below is a monstrosity it needs to be made to actually work
        if len(split_sub) > 3:
            log.error("The domain {0} has too many parts and cannot be processed. Use a simpler domain with MAX 3 parts.".format(_sub))
            raise ValueError("invalid url")
        elif len(split_sub) == 3:
            log.debug("The domain {0} has exactly three parts.".format(_sub))
            return parsed
        elif len(split_sub) == 1:
            log.debug("The domain {0} has exactly one part. Interpreting as a domain name only.".format(_sub))
            return "*.{0}.*".format(split_sub[0])
        elif (len(split_sub) == 2 and split_sub[1] not in tld):
            log.debug("The domain {0} has exactly two parts, and the second part is NOT a top level domain I recognize. Interpreting as a host + a domain name.".format(_sub))
            return "{0}.{1}.*".format(split_sub[0], split_sub[1])
        elif split_sub[1] in tld:
            log.debug("The domain {0} has exactly two parts, and the second part IS a top level domain I recognize. Interpreting as a domain name with a top level domain.".format(_sub))
            return "*.{0}.{1}".format(split_sub[0], split_sub[1])
        #todo add just TLD.

class APConfig(Config):

    def __init__(self, ap_name, ap_password, iface_in="eth0", iface_out="wlan0"):
        super(APConfig, self).__init__()
        self._config_type = "create_ap"
        self.iface_in = iface_in
        self.iface_out = iface_out
        self.header = "{0} {1} ".format(self.iface_out, self.iface_in)
        self.ap_name = ap_name
        self.ap_password = ap_password
        self.add_rule(self.ap_name)
        self.add_rule(self.ap_password)
        self.config_type = "create_ap"

    @property
    def ap_password(self):
        return self._ap_password

    @ap_password.setter
    def ap_password(self, plaintext):
        if (8 < len(str(plaintext)) <= 63 and
            all(char in string.printable for char in plaintext)):
            self._ap_password = plaintext
        else:
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

    def add_rule(self, rule):
        log.debug("adding rule {0}".format(rule))
        self._rules.append("{0} ".format(rule))
