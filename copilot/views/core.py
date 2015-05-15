#Get application content
from copilot import app
from copilot.models.trainer import get_trainer

from flask import render_template, redirect, url_for
from flask.ext.login import login_required, current_user

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

# HTTP error handling
@app.route('/error', defaults={"face": "sad"})
def error(face):
    # current faces designed
    # happy, suprise, sad, FIRE
    return render_template('error.html', face=face)
