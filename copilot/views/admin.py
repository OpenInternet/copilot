#Get application content
from copilot import app, db
from copilot.models import Trainer
#Import forms
from copilot.views.forms import LoginForm

#Get flask modules
from flask import redirect, url_for, render_template, flash
from flask.ext.login import login_user, logout_user, login_required
from copilot.controllers import get_trainer

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #We only have one admin user, so we only query for the first ID in the trainer table
        trainer = get_trainer()
        if trainer.is_correct_password(form.password.data):
            flash("TRAINER PASS CORRECT")
            login_user(trainer)
            flash(login_user(trainer))
            return redirect(url_for('index'))
        else:
            buttons = [{"name":"Submit", "submit":True}]
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()

    return redirect(url_for('index'))


