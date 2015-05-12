#stat logging
import logging
log = logging.getLogger(__name__)

def get_option(package, config):
    """Load an option from a packages config file """
    log.debug("TODO")

def get_config(package="all"):
    """Get a packages config object, or all package config objects.
    Return as a dict, or as a list of dicts if all is chosen.
    """
    log.debug("TODO")

def get_all(option):
    """Returns a list of a specific key's value across all packages config files with no repeats."""
    log.debug("TODO")
