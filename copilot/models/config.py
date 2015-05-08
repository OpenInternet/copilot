import os

#stat logging
import logging
log = logging.getLogger(__name__)

CP_PACKAGES = {"dns":{"name": "dnschef",
                      "config_file": "dnschef.conf",
                      "target" : "dns",
                      "actions": ["block", "redirect"],
                      "directory":"main"},
               "ap":{"name": "create_ap",
                     "config_file": "ap.conf",
                     "directory":"profiles"}}

CP_ACTIONS = ['block']

def get_config_dir(directory):
    directories = {"main":"/tmp/copilot/",
                   "profiles": "/tmp/copilot/profiles"}
    if directory in directories:
        log.debug("Directory {0} found and being returned.".format(directory))
        return directories[directory]
    else:
        raise ValueError("That config directory is not valid.")

def get_config_file(config):
    """ return the path to a config file."""
    _copilot_dir = get_config_dir("main")
    configs = {}
    if config in configs:
        if "config_file" in CP_PACKAGES[config]:
            try:
                _directory = get_config_dir(CP_PACKAGES[config]["directory"])
            except ValueError as err:
                log.error("Directory found in CP_PACKAGES under the {0} package was invalid.".format(config))
                raise ValueError(err)
            log.debug("Returning config path")
            return os.path.join(_directory, CP_PACKAGES[config]["config_file"])
    else:
        raise ValueError("That config file is not valid.")

def get_valid_targets():
    _targets = []
    for item in CP_PACKAGES:
        if "target" in CP_PACKAGES[item]:
            _targets.append(CP_PACKAGES[item]["target"])
    return _targets

def get_valid_actions():
    return CP_ACTIONS


class Config:

    def __init__(self):
        self._rules = []

    @property
    def config_type(self):
        return self._config_type

    @config_type.setter
    def config_file(self, config_type):
        try:
            config_file = get_config_file(config_type)
        except ValueError as err:
            log.error("An invalid config type was passed. Please check \"get_config_file\" in the controllers scripts for the valid types of config files.")
            raise ValueError(err)
        self._config_file = config_file

    def make_main(self):
        log.debug("creating the main config directory if it does not exist.")
        _main_config = get_config_dir("main")
        if not os.path.exists(_main_config):
            os.makedirs(_main_config)

    def check_config_file(self, path):
        self.make_main_config_dir()
        if os.path.exists(path):
            return True
        else:
            return False

    def add_rule(self, rule):
        log.debug("adding rule {0}".format(rule))
        self._rules.append(rule)

    def write_config(self):
        self.write_header()
        for rule in self._rules:
            self.write_rule(rule)

    def write_rule(self, rule):
        with open(self._config_file, 'a') as config_file:
            log.debug("writing rule {0}".format(rule))
            config_file.write(rule)

    def write_header(self):
        log.debug("writing header info {0}".format(self._header))
        with open(self._config_file, 'w') as config_file:
            if self._header:
                log.debug("Found header. Writing to config file {0}".format(config_file))
                config_file.write(self._header)
            else:
                log.debug("No header found. Overwriting config file {0}".format(config_file))
                config_file.write("")


class DNSConfig(Config):

    def __init__(self):
        super(DNSConfig, self).__init__()
        self._config_type = "dnschef"
        self._header = "[A]\n"

    def add_rule(self, rule):
        _rule = ""
        _target = ""
        _address = ""
        try:
            _target = self.get_dns(rule[1])
        except ValueError as err:
            log.warn("Could not add rule. Invalid Target.")
        if rule[0] == "block":
            log.debug("Found a blocking role. Setting address to localhost (127.0.0.1).")
            _address = "127.0.0.1"
        elif rule[0] == "redirect":
            log.debug("Found a redirection role. Setting address to default AP address (192.168.12.1).")
            _address = "192.168.12.1"
        _rule = "{0} = {1}\n".format(_target, _address)
        self.rules.append(_rule)

    def get_dns(self):
        tld = ["ac", "ad", "ae", "aero", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "arpa", "as", "asia", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "biz", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cat", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "com", "coop", "cr", "cs", "cu", "cv", "cw", "cx", "cy", "cz", "dd", "de", "dj", "dk", "dm", "do", "dz", "ec", "edu", "ee", "eg", "eh", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gov", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "info", "int", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jobs", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "local", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mil", "mk", "ml", "mm", "mn", "mo", "mobi", "mp", "mq", "mr", "ms", "mt", "mu", "museum", "mv", "mw", "mx", "my", "mz", "na", "name", "nato", "nc", "ne", "net", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "onion", "org", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "pro", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tel", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "travel", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "xxx", "ye", "yt", "yu", "za", "zm", "zr", "zw"]
        _sub = self.sub_target
        log.debug("sub target is {0}".format(_sub))
        if _sub == "":
            return None
        parsed = urlparse(_sub).path
        log.debug("parsed url is {0}".format(parsed))
        split_sub = string.split(parsed, ".")
        log.debug("split up sub target is {0}".format(split_sub))
        #TODO the below is a monstrosity
        if len(split_sub) > 3:
            raise ValueError("invalid url")
        elif len(split_sub) == 3:
            return parsed
        elif len(split_sub) == 1:
            return "*.{0}.*".format(split_sub[0])
        elif (len(split_sub) == 2 and split_sub[1] not in tld):
            return "{0}.{1}.*".format(split_sub[0], split_sub[1])
        elif split_sub[1] in tld:
            return "*.{0}.{1}".format(split_sub[0], split_sub[1])
        #todo add just TLD.
