#Get application content
from copilot import app
from copilot.models.trainer import get_trainer
from copilot.utils.plugin import is_service
from flask import render_template, redirect, url_for, flash
from flask.ext.login import login_required, current_user
from copilot.models.trainer import get_ap_status
from copilot.models.profile import get_profile_status

import subprocess
import re

#stat logging
import logging
log = logging.getLogger(__name__)


@app.route('/')
def index():
    """ Redirects user to the correct base page.

    Redirects the user to their profile, the login page
    or the initial configuration page based upon if there
    is a trainer user created and if the user is authenticated
    as that trainer.
    """
    log.info("root route requested")
    log.debug(current_user.is_authenticated)
    if current_user.is_authenticated:
        log.debug("user is authenticated.")
        return redirect(url_for('profile'))
    elif get_trainer():
        log.debug("there is a trainer currently")
        return redirect(url_for('login'))
    else:
        log.debug("No trainer exists. Setting up congfig.")
        return redirect(url_for('config'))

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
    """ The route for pages that are not found"""
    log.debug("This page cannot be found")
    flash("We're sorry. The page you are looking for cannot be found.", "error")
    return redirect(url_for("profile"))

@app.route('/menu')
@login_required
def menu():
    """ Menu Route

    TODO This route needs to be deleted in the future.
    https://github.com/OpenInternet/co-pilot/issues/110
    """
    return render_template('menu.html')

@app.route('/info')
@login_required
def info():
    """ CoPilot current configuration information interface

    An info page that gives the current status of the co-pilot device.
    https://github.com/OpenInternet/co-pilot/wiki/User-Interface-Elements#info
    """
    profile = get_profile_status()
    access_point = get_ap_status()
    status = [{"icon" : "vpn_lock",
               "name" : "Profile",
              "value" : profile['value'],
              "status" : profile['status'],
               "url" : "profile_current"},
              {"icon":"wifi_tethering",
               "name" : "Access Point Name",
               "value":access_point['value'],
               "status":access_point['status'],
               "url":"config"}]
    return render_template('info.html', status=status, title="Co-Pilot Info")


# HTTP error handling
@app.route('/error', defaults={"face": "sad"})
@app.route('/error/<face>')
def error(face):
    """ The Error Interface.

    The error page for when something goes wrong with co-pilot.
    https://github.com/OpenInternet/co-pilot/wiki/User-Interface-Elements#error

    Args:
        face (str): The expression to use on the CoPilot avatar's face.
            - Options include sad, suprise, happy, and fire.
    """
    face = face.decode("UTF-8")
    # current faces designed
    # happy, suprise, sad, fire
    emotes = {"sad":"frown",
              "suprise":"oface",
              "happy":"smile",
              "fire":"fire"}
    if face in emotes:
        emotion = emotes[face]
    else:
        emotion = "smile"
    return render_template('error.html', emotion=emotion)
