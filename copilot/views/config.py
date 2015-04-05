#Get application content
from copilot import app, db
from copilot.controllers import get_trainer, get_status_items

import subprocess
#Import forms
from copilot.views.forms import Config, AdminConfig
from copilot.models import Trainer

#Get flask modules
from flask import redirect, url_for, render_template, flash
from flask.ext.login import login_user, login_required

@app.route('/config/initial', methods=["GET", "POST"])
def config_initial():
    """The iniital configuration menu for  """
    form = InitialConfig()
    # If there is currently a trainer configured redirect away from this page
    if get_trainer():
        return redirect(url_for('index'))
    if form.validate_on_submit():
        trainer = Trainer(trainer_pass=form.password.data, ap_name=form.ap_name.data, ap_password=form.ap_password.data)
        db.session.add(trainer)
        db.session.commit()
        trainer.write_ap_config()
        subprocess.call(["service", "create_ap", "restart"])
        login_user(trainer)
        flash('Your configuration has been set!')
        return redirect(url_for('index'))

    return render_template('initial_config.html', form=form)

@app.route('/config/admin', methods=["GET", "POST"])
@login_required
def config_admin():
    form = AdminConfig()
    if form.validate_on_submit():
        trainer = get_trainer()
        if form.password.data != "":
            flash("set password")
            trainer.password = form.password.data
        if form.ap_name.data != "":
            flash("set ap name")
            trainer.ap_name = form.ap_name.data
        if form.ap_password.data != "":
            flash("set ap password")
            trainer.ap_password = form.ap_password.data
        db.session.commit()
        trainer.write_ap_config()
        subprocess.call(["service", "create_ap", "restart"])
        return redirect(url_for('index'))

    return render_template('admin_config.html', form=form)

@app.route('/config', methods=["GET", "POST"])
def config():
    print("Starting")
    trainer_exists = get_trainer()
    #If there is already a trainer setup on the box then provide the admin configuration.
    if trainer_exists:
        print("01 trainer exists")
        form = AdminConfig()
    else:
        print("02 trainer DOES NOT exists")
        form = Config()
    if form.validate_on_submit():
        print("FORM IS VALID")
        #Add any new values to the existing trainer
        if trainer_exists:
            trainer = trainer_exists
            if form.password.data != "":
                flash("set password")
                trainer.password = form.password.data
            if form.ap_name.data != "":
                flash("set ap name")
                trainer.ap_name = form.ap_name.data
            if form.ap_password.data != "":
                flash("set ap password")
                trainer.ap_password = form.ap_password.data
        #Create the trainer if one does not exist
        else:
            trainer = Trainer(trainer_pass=form.password.data, ap_name=form.ap_name.data, ap_password=form.ap_password.data)
        #Write values and send the user back to main index.
        print("Committing Session File")
        db.session.commit()
        print("Writing Config File")
        trainer.write_ap_config()
        print("Restarting create_ap")
        subprocess.call(["service", "create_ap", "restart"])
        print("Redirecting to index.")
        return redirect(url_for('index'))
    else:
        print("DID NOT VALIDATE")
        print("ERRORS: {0}".format(form.errors))
    status_items = get_status_items()
    buttons = [{"name":"Submit", "submit":True}]
    print("Rendering config.")
    return render_template('config.html', form=form, trainer_exists=trainer_exists, status_items=status_items, buttons=buttons)
