from copilot.models.config import Config
from exceptions import ValueError

import string
from urlparse import urlparse

class ConfigWriter(Config):

    def __init__(self):
        super(ConfigWriter, self).__init__()
        self.log.debug("Initializing dns config writer.")
        self.config_type = "dns"
        self.header = "[A]\n"

    def add_rule(self, rule):
        action, target, sub = rule[0], rule[1], rule[2]
        self.log.debug("Adding rule {0} {1} {2}".format(action, target, sub))
        _rule = ""
        _domain = ""
        _address = ""
        try:
            _domain = self.get_dns(sub)
        except ValueError as err:
            self.log.warning("Could not add rule. Invalid Target.")
            raise ValueError(err)
        if action == "block":
            self.log.debug("Found a blocking role. Setting address to localhost (127.0.0.1).")
            _address = "127.0.0.1"
        elif action == "redirect":
            self.log.debug("Found a redirection role. Setting address to default AP address (192.168.12.1).")
            _address = "192.168.12.1"
        _rule = "{0} = {1}\n".format(_domain, _address)
        self._rules.append(_rule)

    def get_dns(self, sub):
        tld = ["ac", "ad", "ae", "aero", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "arpa", "as", "asia", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "biz", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cat", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "com", "coop", "cr", "cs", "cu", "cv", "cw", "cx", "cy", "cz", "dd", "de", "dj", "dk", "dm", "do", "dz", "ec", "edu", "ee", "eg", "eh", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gov", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "info", "int", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jobs", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "local", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mil", "mk", "ml", "mm", "mn", "mo", "mobi", "mp", "mq", "mr", "ms", "mt", "mu", "museum", "mv", "mw", "mx", "my", "mz", "na", "name", "nato", "nc", "ne", "net", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "onion", "org", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "pro", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tel", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "travel", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "xxx", "ye", "yt", "yu", "za", "zm", "zr", "zw"]
        _sub = sub
        self.log.debug("sub target is {0}".format(_sub))
        if _sub == "":
            return None
        parsed = urlparse(_sub).path
        self.log.debug("parsed url is {0}".format(parsed))
        split_sub = string.split(parsed, ".")
        self.log.debug("split up sub target is {0}".format(split_sub))
        #TODO the below is a monstrosity it needs to be made to actually work
        if len(split_sub) > 3:
            self.log.error("The domain {0} has too many parts and cannot be processed. Use a simpler domain with MAX 3 parts.".format(_sub))
            raise ValueError("invalid url")
        elif len(split_sub) == 3:
            self.log.debug("The domain {0} has exactly three parts.".format(_sub))
            return parsed
        elif len(split_sub) == 1:
            self.log.debug("The domain {0} has exactly one part. Interpreting as a domain name only.".format(_sub))
            return "*.{0}.*".format(split_sub[0])
        elif (len(split_sub) == 2 and split_sub[1] not in tld):
            self.log.debug("The domain {0} has exactly two parts, and the second part is NOT a top level domain I recognize. Interpreting as a host + a domain name.".format(_sub))
            return "{0}.{1}.*".format(split_sub[0], split_sub[1])
        elif split_sub[1] in tld:
            self.log.debug("The domain {0} has exactly two parts, and the second part IS a top level domain I recognize. Interpreting as a domain name with a top level domain.".format(_sub))
            return "*.{0}.{1}".format(split_sub[0], split_sub[1])
        #todo add just TLD.


def setup(app):
    app.get_config_writer(ConfigWriter)
