#Get application content
from copilot import app, db
from copilot.models import Trainer, Profile

#Get flask modules
from flask import redirect, url_for, render_template, flash
from flask.ext.login import login_user, login_required

@app.route('/profile/new', methods=["GET", "POST"])
@login_required
def profile_new():
    """Display an empty profile editor."""
    profile = Profile("new")
    profile.save()
    return render_template('profile_edit.html', profile=profile)

@app.route('/profile/edit/<string:prof_name>', methods=["GET", "POST"])
@login_required
def profile_edit():
    """Display an existing profle in the profile editor."""

    return render_template('profile_edit.html', form=form)

@app.route('/profile/save', methods=["GET", "POST"])
@login_required
def profile_save():
    """Display the profile that is currently being run on the Co-Pilot box. """

    return render_template('profile_save.html', form=form)

@app.route('/profile/load', methods=["GET", "POST"])
@login_required
def profile_load():
    """Display the profile that is currently being run on the Co-Pilot box. """

    return render_template('profile_load.html', form=form)

@app.route('/profile/current', methods=["GET", "POST"])
@login_required
def profile_current():
    """Display the profile that is currently being run on the Co-Pilot box. """

    return render_template('profile_current.html', form=form)

