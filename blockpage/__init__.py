# -*- coding: utf-8 -*-

#import flask
from flask import Flask

import logging
#set logger
logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
lhr = logging.FileHandler("/var/log/blockpage.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
lhr.setFormatter(formatter)
logger.addHandler(lhr)

# If we set instance_relative_config=True when we create our app with the Flask() call, app.config.from_pyfile() will load the specified file from the instance/ directory.
blockpage = Flask('blockpage', instance_relative_config=True)
#blockpage.config.from_object('config')
# Load configuration variables from an instance folder.
blockpage.config.from_pyfile('bp_config.py')

#Putting the import at the end avoids the circular import error.
from blockpage import models
from blockpage import controllers
from blockpage import views
