# -*- coding: utf-8 -*-

#Get application content
from copilot import app, db
from copilot.models import profile as mdl_prof
from copilot.views import forms
from flask.ext.wtf import Form
from copilot.controllers import get_status_items
from copilot.models.config import get_valid_actions, get_valid_targets, get_config_dir
from copilot.models.trainer import get_trainer
from copilot.utils.file_sys import get_usb_dirs
#Get flask modules
from flask import redirect, url_for, render_template, flash, make_response, request
from flask.ext.login import login_user, login_required
from wtforms import FormField

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

    #Get what submit button the user pressed
    _save = False
    _apply = False
    _download = False
    log.info("Checking users submission choice.")
    if request.form['submit_action'] == 'Save':
        _save = True
    elif request.form['submit_action'] == 'Save & Apply':
        _save = True
        _apply = True
    elif request.form['submit_action'] == 'Apply':
        _apply = True
    elif request.form['submit_action'] == 'Download':
        _download = True
    elif request.form['submit_action'] == 'Load':
        return redirect(url_for('profile_load'))

    form = forms.NewProfileForm()
    if form.validate_on_submit():
        log.info("profile form is valid")
        log.debug("Form {0} submitted".format(form.prof_name.data))
        prof_name = form.prof_name.data
        profile = mdl_prof.Profile(prof_name)
        for rule in form.data['rules']:
            _rule = mdl_prof.Rule(rule['target'], rule['action'], rule['sub_target'])
            profile.add_rule(_rule)
        log.debug("Saving profile in temporary directory {0}".format(prof_name))
        profile.profile_dir = "temporary"
        profile.save()
        if _download:
            profile_file = open(profile.profile_dir + profile.name)
            response = make_response(profile_file)
            response.headers["Content-Disposition"] = "attachment; filename={0}".format(profile.name)
            return response
        if _apply:
            profile.apply_config()
        if _save:
            return redirect(url_for('profile_save', profile=prof_name))
        elif _apply:
            flash('Profile "{0}" has been applied!'.format(prof_name), 'success')
    else:
        log.info("Form was not validated or not specified.")
        log.debug(form.errors) #Log errors if they exist
        log.info("No profile was passed... loading up profile for display.")
        profile = mdl_prof.Profile(prof_name)
        if profile.exist():
            log.info("Existing profile found. Loading profile")
            log.debug("Loading rule {0}".format(prof_name))
            profile.load()
            form.prof_name.data = profile.name
            log.info("Adding profile rules.")
            for rule in profile.rules:
                log.debug("adding rule: action: {0}, target:{1}, subtarget{2}".format(rule.action, rule.target, rule.sub_target))
                form.rules.append_entry(data={"target":rule.target, "sub_target":rule.sub_target, "action":rule.action})
        else:
            log.info("New profile being created")
            form = forms.NewProfileForm()
            form.rules.append_entry(data={"target":get_valid_targets(), "sub_target":"internews.org", "action":get_valid_actions()})
            form.prof_name.data = "new"
            log.debug(dir(form.rules))
    status_items = get_status_items()
    buttons = [{"name":"Download", "submit":True},
               {"name":"Load", "submit":True},
               {"name":"Save", "submit":False},
               {"name":"Apply", "submit":False},
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

    log.info("Checking users submission choice.")
    if request.form['submit_action'] == 'Upload Profile':
        tmp_profile = mdl_prof.Profile("tmp")
        tmp_profile.profile_dir = "temporary"
        user_file = request.files['Profile']
        _profile_loc = os.path.join(tmp_profile.profile_dir, tmp_profile.name)
        log.debug("Saving user supplied configuration in {0}".format(_profile_loc))
        user_file.save(_profile_loc)
        try:
            #get correct info (and name) from file.
            tmp_profile.refresh()
        except ValueError as err:
            flash("That is not a valid co-pilot config file.", "error")
            return redirect(url_for('profile_load'))
        tmp_profile.profile_dir = "profiles"
        tmp_profile.save()
        tmp_profile.apply_config()
        return redirect(url_for('profile', prof_name=tmp_profile.name))

    profiles = mdl_prof.get_all_profiles()
    if profiles = []:
        flash('You don\'t seem to have any profiles saved on this device.', 'error')
        flash('You can still create a new profile!', 'success')
        redirect(url_for('error', face="suprise"))

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
    profile = mdl_prof.Profile(prof_applied)
    profile.load()
    status_items = get_status_items()
    buttons = [{"name":"Return", "link":url_for('profile')}]
    return render_template('profile_applied.html', profile=profile, buttons=buttons, status_items=status_items)

@app.route('/profile/save', defaults={"prof_name": "null"}, methods=["GET", "POST"])
@login_required
def profile_save(prof_name):
    """Choose where to save the current profile."""

    form = forms.SavePeofileForm()
    if form.validate_on_submit():
        log.info("save form is valid")
        log.info("identifying the directory to save to.")
        save_loc = form.location.data
        if save_loc == "Co-Pilot":
            save_dir = get_config_dir("profiles")
        elif save_dir in get_usb_dirs():
            save_dir = form.location.data
        else:
            log.debug("See! This is why we don't accept user input. I gave you just fine USB directories, and you give me this. What do you want me to do with this?")
            flash("Directory {0} does not exist. Cannot save a profile to a non-existant folder, non mounted USB drive, or un-allowed folder. Did you unplug the usb between page loads?".format(save_loc), "error")
            redirect(url_for('error'))

        prof_name = form.prof_name.data
        profile = mdl_prof.Profile(prof_name)
        profile.profile_dir = "temporary"
        profile.refresh()
        profile.profile_dir = "profiles"
        profile.save()
    else:
        if prof_name != "null":
            form.prof_name.data = prof_name
        else:
            flash('An error occured identifying the profile to save.', 'error')
            redirect(url_for('error'))

    status_items = get_status_items()
    buttons = [{"name":"Save", "submit":True}]
    return render_template('profile.html',
                           status_items=status_items,
                           buttons=buttons)
