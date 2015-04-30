# -*- coding: utf-8 -*-

#import flask
from flask import Flask

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

#import Bcrypt
from flask.ext.bcrypt import Bcrypt

import logging
#set logger
logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
lhr = logging.FileHandler("/var/log/copilot.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
lhr.setFormatter(formatter)
logger.addHandler(lhr)

# If we set instance_relative_config=True when we create our app with the Flask() call, app.config.from_pyfile() will load the specified file from the instance/ directory.
app = Flask('copilot', instance_relative_config=True)
app.config.from_object('config')
# Load configuration variables from an instance folder.
app.config.from_pyfile('config.py')

#Define the Bcrypt object
bcrypt = Bcrypt(app)

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Putting the import at the end avoids the circular import error.
# Wow do I have to fix these * imports
from copilot.models import *
from copilot import controllers
from copilot.views import *


# Build the database
db.create_all()
