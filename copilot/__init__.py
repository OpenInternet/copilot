# -*- coding: utf-8 -*-

#import flask
from flask import Flask

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

#import Bcrypt
from flask.ext.bcrypt import Bcrypt

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

#Putting the import at the end avoids the circular import error.
from copilot import models
from copilot import controllers
from copilot.views import core, admin, config, profile


# Build the database
db.create_all()

