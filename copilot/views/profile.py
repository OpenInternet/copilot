# -*- coding: utf-8 -*-

#Get application content
from copilot import app, db, models
from copilot.models import get_valid_actions, get_valid_targets
from copilot.views import forms
from flask.ext.wtf import Form


#Get flask modules
from flask import redirect, url_for, render_template, flash
from flask.ext.login import login_user, login_required
from wtforms import FormField
from copilot.controllers import get_trainer, get_status_items

from os import listdir
from os.path import isfile, join

#stat logging
import logging
log = logging.getLogger(__name__)


@app.route('/profile', defaults={"prof_name": "null"},  methods=["GET", "POST"])
@app.route('/profile/edit/<string:prof_name>', methods=["GET", "POST"])
@login_required
def profile(prof_name):
    """Display an existing profle in the profile editor."""
    log.debug("profile received {0}".format(prof_name))
    form = forms.NewProfileForm()
    if form.validate_on_submit():
        log.info("profile form was validated")
        log.debug("Form {0} submitted".format(form.prof_name.data))
        prof_name = form.prof_name.data
        profile = models.Profile(prof_name)
        for rule in form.data['rules']:
            _rule = models.Rule(rule['target'], rule['action'], rule['sub_target'])
            profile.add_rule(_rule)
        profile.save()
        #Save as current profile for trainer.
        #TODO make this change depending upon the submit button used
        trainer = get_trainer()
        log.debug(form.data)
        trainer.current = form.data['prof_name']
        db.session.commit()
        profile.apply_it()
        flash('Your profile has been saved and Applied!')
        return redirect(url_for('profile_applied'))
    else:
        log.info("Form was not validated.")
        log.debug(form.errors)
        profile = models.Profile(prof_name)
        if profile.exist():
            log.debug("Loading rule {0}".format(prof_name))
            profile.load()
            form.prof_name.data = profile.name
            for rule in profile.rules:
                log.debug("adding rule: action: {0}, target:{1}, subtarget{2}".format(rule.action, rule.target, rule.sub_target))
                form.rules.append_entry(data={"target":rule.target, "sub_target":rule.sub_target, "action":rule.action})
        else:
            log.debug("New profile being created")
            form = forms.NewProfileForm()
            form.rules.append_entry(data={"target":"dns", "sub_target":"internews.org", "action":"block"})
            form.prof_name.data = "new"
            log.debug(dir(form.rules))
    status_items = get_status_items()
    buttons = [{"name":"Submit", "submit":False},
               {"name":"Test", "submit":False},
               {"name":"Save", "submit":False},
               {"name":"Save & Apply", "submit":True}]
    return render_template('profile.html',
                           form=form,
                           status_items=status_items,
                           buttons=buttons)


@app.route('/profile/current', methods=["GET", "POST"])
@login_required
def profile_current():
    """Display the profile that is currently being run on the Co-Pilot box. """
    #Check for profile_edit
    trainer = get_trainer()
    #populate from trainer if possible
    current = trainer.current
    if current:
        return redirect(url_for('profile', prof_name=current))
    else:
        return redirect(url_for('profile'))

@app.route('/profile/load', methods=["GET", "POST"])
@login_required
def profile_load():
    """Display the profile that is currently being run on the Co-Pilot box. """
    PROFILE_DIR="/tmp/copilot/profiles/"
    profiles = [ f for f in listdir(PROFILE_DIR) if isfile(join(PROFILE_DIR,f)) ]
    status_items = get_status_items()
    buttons = [{"name":"Return", "link":url_for('profile')}]
    return render_template('load.html',
                           profiles=profiles,
                           status_items=status_items,
                           buttons=buttons)


@app.route('/profile/applied', methods=["GET", "POST"])
@login_required
def profile_applied():
    """Display an empty profile editor."""
    #Check for profile_edit
    trainer = get_trainer()
    #populate from trainer if possible
    prof_applied = trainer.current
    log.debug(prof_applied)
    # if none send trainer to create a new one.
    if prof_applied == None:
        return redirect(url_for('profile'))
    profile = models.Profile(prof_applied)
    profile.load()
    status_items = get_status_items()
    buttons = [{"name":"Return", "link":url_for('profile')}]
    return render_template('profile_applied.html', profile=profile, buttons=buttons, status_items=status_items)

@app.route('/profile/save', methods=["GET", "POST"])
@login_required
def profile_save():
    """Display the profile that is currently being run on the Co-Pilot box. """

    return render_template('profile_save.html', form=form)

