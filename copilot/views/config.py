#Get application content
from copilot import app, db
from copilot.models.trainer import get_trainer

import subprocess
#Import forms
from copilot.views.forms import Config, AdminConfig
from copilot.models.trainer import Trainer
from copilot.controllers import flash_errors
from copilot.models.config import get_config_writer, get_plugins_with_advanced_config_pages
#Get flask modules
from flask import redirect, url_for, render_template, flash
from flask.ext.login import login_user, login_required

#stat logging
import logging
log = logging.getLogger(__name__)

@app.route('/config', methods=["GET", "POST"])
def config():
    """ The configuration interface.

    This route includes both the initial configuration interface
    as well as the administrative configuration interface. The interface
    is chosen based upon the existance of a trainer. If there is already a
    trainer setup on CoPilot then the administrative interface is provided.
    If there is not an existing trainer than the initial configuration
    interface is provided.
    """
    log.debug("Starting configuration interface")
    trainer_exists = get_trainer()
    #If there is already a trainer setup on the box then provide the admin configuration.
    if trainer_exists:
        log.info("Trainer exists")
        form = AdminConfig()
    else:
        log.info("Trainer does not exist")
        form = Config()
    if form.validate_on_submit():
        #Add any new values to the existing trainer
        if trainer_exists:
            log.debug("Found a trainer. Modifying existing configuration.")
            trainer = trainer_exists
            if form.password.data != "":
                flash("set password")
                trainer.password = form.password.data
                db.session.commit()
            if form.ap_name.data != "":
                flash("setting ap name to {0}".format(form.ap_name.data))
                trainer.ap_name = form.ap_name.data
                db.session.commit()
                trainer.ap_config = get_config_writer("create_ap")
                trainer.ap_config.add_rule(form.ap_name.data, trainer.ap_password)
                trainer.ap_config.write()
            if form.ap_password.data != "":
                flash("set ap password")
                trainer.ap_config = get_config_writer("create_ap")
                trainer.ap_name = form.ap_password.data
                db.session.commit()
                trainer.ap_config.add_rule(trainer.ap_name, form.ap_password.data)
                trainer.ap_config.write()
        #Create the trainer if one does not exist
        else:
            log.debug("No trainer found. Creating a new configuration.")
            trainer = Trainer(trainer_pass=form.password.data, ap_name=form.ap_name.data, ap_password=form.ap_password.data)
            db.session.add(trainer)

            #Write values and send the user back to main index.
            log.info("Committing Session File")
            db.session.commit()
            log.info("Writing Config File")
            trainer.ap_config.write()
            log.info("Restarting create_ap")
            subprocess.call(["/usr/sbin/service", "create_ap", "restart"], shell=True)
            login_user(trainer)
            log.info("Redirecting to index.")
            return redirect(url_for('index'))
    else:
        log.debug("configuration file was not valid.")
        flash_errors(form)

    buttons = [{"name":"Submit", "submit":True}]
    return render_template('config.html', form=form, trainer_exists=trainer_exists, buttons=buttons, title="Settings")


## ============================
#  Plugins
## ============================

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
    return render_template('plugins.html',
                           services=services,
                           title="Service Status/Restart")

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

# @app.route('/plugins/configure')
# @login_required
# def plugin_configuration_picker(plugin_name):
#     """List of plugin advanced configuration pages

#     Args:
#         service (str): The name of a service to be restarted.
#     """
#     plugins = get_plugins_with_advanced_config_pages()


@app.route('/plugins/configure/<string:prof_name>')
@login_required
def configure_plugin(plugin_name):
    """CoPilot plugin advanced configuration page

    Args:
        service (str): The name of a service to be restarted.
    """
    log.debug("plugin {0} has an advanced configuration page".format(plugin.name))
    form = plugin.get_config_form()
    form_config = {}
    form_config.setdefault("name", url_for("save_plugin_config") + "/" + plugin_name)
    title="{0} Advanced Configuration Page".format(plugin_name)
    plugin = get_plugin(plugin_name)
    if plugin.has_configuration_page is True:
        form_config.setdefault("has_form", True)
    else:
        form_config.setdefault("has_form", False)
    return render_template("plugin_adv_config.html",
                           form=form,
                           title=title,
                           plugin_name=plugin_name,
                           form_config=form_config)

@app.route('/plugins/configure/save/<string:plugin_name>')
@login_required
def save_plugin_config(plugin_name):
    """CoPilot plugin advanced  configuration page

    Args:
        service (str): The name of a service to be restarted.
    """
    raise NotImplementedError("")
