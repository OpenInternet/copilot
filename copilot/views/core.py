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
    flash("We're sorry. The page you are looking for cannot be found.", "error")
    return redirect(url_for("error", face="sad"))

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
    status = [{"icon" : "profile",
               "name" : "Profile",
              "value" : profile['value'],
              "status" : profile['status'],
               "url" : "profile_current"},
              {"icon":"wifi",
               "name" : "Access Point Name",
               "value":access_point['value'],
               "status":access_point['status'],
               "url":"config"}]
    return render_template('info.html', status=status, title="Co-Pilot Info")

@app.route('/plugins')
@login_required
def plugins():
    """ CoPilot plugin status and management interface

    An page that displays all the current co-pilot services and
    allows the trainer to restart them if they are acting up.
    https://github.com/OpenInternet/co-pilot/wiki/User-Interface-Elements#plugins

    """
    services = {}
    for line in subprocess.check_output(['supervisorctl', 'status']).split('\n'):
        log.debug("Service line received: {0}".format(line))
        match_name = re.search("^([^\s]*)\s*([A-Z]*)", line)
        if match_name and match_name.group(1) != "":
            name = match_name.group(1)
            running = match_name.group(2)
            services[name] = running
    return render_template('plugins.html', services=services, title="Service Status/Restart")

@app.route('/plugins/restart/<service>')
@login_required
def restart_service(service):
    """ A route that will restart a service.

    If the plugins/restart/ route is appended with the
    name of a CoPilot service and accessed by a logged in
    user CoPilot will restart that service.

    See the plugins interface for usage.

    Args:
        service (str): The name of a service to be restarted.
    """
    if is_service(service):
        subprocess.call(["supervisorctl", "restart", service])
    flash("Service {0} restarted.".format(service), "success")
    return redirect(url_for("plugins"))


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
