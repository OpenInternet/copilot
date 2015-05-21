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
    print(current_user.is_authenticated())
    if current_user.is_authenticated():
        print("user is authenticated.")
        return redirect(url_for('profile'))
    elif get_trainer():
        print("there is a trainer currently")
        return redirect(url_for('login'))
    else:
        print("No trainer exists. Setting up congfig.")
        return redirect(url_for('config'))

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/menu')
@login_required
def menu():
     return render_template('menu.html')

@app.route('/info')
@login_required
def info():
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
    if is_service(service):
        subprocess.call(["supervisorctl", "restart", service])
    flash("Service {0} restarted.".format(service), "success")
    return redirect(url_for("plugins"))

# HTTP error handling
@app.route('/error', defaults={"face": "sad"})
@app.route('/error/<face>')
def error(face):
    face = face.decode("UTF-8")
    # current faces designed
    # happy, suprise, sad, fire
    emotes = {"sad":"emote_frown",
              "suprise":"emote_oface",
              "happy":"emote_smile"}
    if face == "fire":
        emotions = ["emote_flame", "emote_smile"]
    else:
        emotions = [emotes[face]]
    return render_template('error.html', emotions=emotions)
