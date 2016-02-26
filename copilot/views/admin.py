#Get application content
from copilot import app, db
from copilot.models.trainer import Trainer
#Import forms
from copilot.views.forms import LoginForm

#Get flask modules
from flask import redirect, url_for, render_template, flash
from flask.ext.login import login_user, logout_user, login_required
from copilot.models.trainer import get_trainer

#stat logging
import logging
log = logging.getLogger(__name__)

@app.route('/login', methods=["GET", "POST"])
def login():
    """The login interface.

    Once Co-Pilot has been set-up, this is the login interface
    the trainer will see.

    https://github.com/OpenInternet/co-pilot/wiki/User-Interface-Elements#log-in-page
    """
    log.debug("logging user in")
    form = LoginForm()
    if form.validate_on_submit():
        #We only have one admin user, so we only query for the first ID in the trainer table
        trainer = get_trainer()
        if trainer.is_correct_password(form.password.data):
            log.debug("User supplied a correct password.")
            login_user(trainer)
            log.debug("User logged in.")
            return redirect(url_for('index'))
        else:
            log.debug("User supplied an incorrect password.")
            flash("The password provided was incorrect. Please try again", "error")
            return redirect(url_for('login'))
    buttons = [{"name":"Submit", "submit":True}]
    return render_template('login.html', form=form, buttons=buttons)

@app.route('/logout')
def logout():
    """ The logout Interface.

    When a user clicks the logout button this route will log them
    out and then redirect them back to the index.
    """
    log.debug("logging user out")
    logout_user()
    log.debug("user logged out")
    return redirect(url_for('index'))
