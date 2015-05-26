# -*- coding: utf-8 -*-

#Get application content
from copilot import app, db
from copilot.models import profile as mdl_prof
from copilot.views import forms

from flask.ext.wtf import Form
from copilot.models.config import get_valid_actions, get_valid_targets, get_config_dir, get_target_by_actions
from copilot.models.trainer import get_trainer
from copilot.utils.file_sys import get_usb_dirs, get_likely_usb, is_usb

#Get flask modules
from flask import redirect, url_for, render_template, flash, make_response, request, send_file
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

    form = forms.NewProfileForm()
    profile = mdl_prof.Profile(prof_name)
    if profile.exist():
        title = "Profile > Edit"
        log.info("Existing profile found. Loading profile")
        log.debug("Loading rule {0}".format(prof_name))
        profile.load()
        form.prof_name.data = profile.name
        log.info("Adding profile rules.")
        for rule in profile.rules:
            _action = rule[0]
            _tar = rule[1]
            _sub = rule[2]
            log.debug("adding rule: action: {0}, target:{1}, subtarget{2}".format(_action, _tar, _sub))
            form.rules.append_entry(data={"target":_tar, "sub_target":_sub, "action":_action})
    else:
        log.info("New profile being created")
        title = "Profile > New"
        form = forms.NewProfileForm()
        _targets = get_valid_targets()
        _actions = get_valid_actions()
        log.debug("Setting default rule target and action. Targets = {0}, Actions = {1}".format(_targets, _actions))
        form.rules.append_entry(data={"target":_targets[0], "sub_target":"internews.org", "action":_actions[0]})
        form.prof_name.data = "new"

    #Add the locations a user can save to.
    locations =["Co-Pilot", "Download"]
    if is_usb():
        locations.append("USB")
    action_pairs = get_target_by_actions()
    all_targets = get_valid_targets()
    return render_template('profile.html',
                           title=title,
                           form=form,
                           locations=locations,
                           action_pairs=action_pairs,
                           all_targets=all_targets)

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

@app.route('/profile/upload', methods=["POST"])
@login_required
def profile_upload():

    log.info("Checking users submission choice.")
    tmp_profile = mdl_prof.Profile("tmp")
    tmp_profile.profile_dir = "temporary"
    tmp_profile.save()
    user_file = request.files['file']
    _profile_loc = join(tmp_profile.profile_dir, tmp_profile.name)
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
    flash("Profile {0} uploaded.".format(tmp_profile.name))
    return redirect(url_for('profile', prof_name=tmp_profile.name))

@app.route('/profile/load', methods=["GET", "POST"])
@login_required
def profile_load():
    """Display the profile that is currently being run on the Co-Pilot box. """

    profiles = mdl_prof.get_all_profiles()
    if profiles == []:
        flash('You don\'t seem to have any profiles saved on this device.', 'error')
        flash('To create a new profile choose "New" in the menu on the top left.', 'success')
        return redirect(url_for('error', face="suprise"))

    return render_template('load.html',
                           title="Profile > Load",
                           profiles=profiles)


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
    buttons = [{"name":"Return", "link":url_for('profile')}]
    return render_template('profile_applied.html', profile=profile, buttons=buttons, title="Profile > Applied")

@app.route('/profile/save', methods=["GET", "POST"])
@login_required
def profile_save():
    """Choose where to save the current profile."""

    form = forms.NewProfileForm()
    if form.validate_on_submit():
        log.info("Profile form is valid")

        log.info("identifying the directory to save to.")
        save_dir = None
        _download = False
        log.info("Checking users submission choice.")
        if request.form['submit_action'] == 'USB':
            save_dir = "usb"
        elif request.form['submit_action'] == 'Co-Pilot':
            save_dir = "profiles"
        elif request.form['submit_action'] == 'Download':
            save_dir = "profiles"
            _download = True
        else:
            log.debug("See! This is why we don't accept user input. I gave you just fine USB directories, and you give me this. What do you want me to do with this?")
            flash("Location {0} does not exist. Cannot save a profile to a non-existant folder, non mounted USB drive, or un-allowed folder. Did you unplug the usb between page loads?".format(save_dir), "error")
            return redirect(url_for('error'))

        prof_name = form.prof_name.data
        profile = mdl_prof.Profile(form.prof_name.data)
        profile.profile_dir = save_dir
        for rule in form.data['rules']:
            profile.add_rule(rule)
        profile.save()
        profile.apply_config()

        log.debug("Applying form data to trainer {0}".format(form.data))
        trainer = get_trainer()
        trainer.current = form.data['prof_name']
        db.session.commit()

        if _download == True:
            return send_file(profile.profile_file, as_attachment=True)

        flash('Profile "{0}" has been applied!'.format(form.prof_name.data), 'success')
        return redirect(url_for('profile_current'))

    else:
        log.debug(form.errors)
        flash('We could not save your profile at this time. It seems to be invalid, but we don\'t know how.', 'error')
        return redirect(url_for('error'))
