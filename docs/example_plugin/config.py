from copilot.models.config import Config

import logging
log = logging.getLogger(__name__)

class ConfigWriter(Config):

    def __init__(self):
        super(ConfigWriter, self).__init__()
        log.info("example config loaded.")
