#Get application content
from copilot import app
from copilot.controllers import get_trainer

from flask import render_template, redirect, url_for
from flask.ext.login import login_required, current_user

@app.route('/')
def index():
    print(current_user.is_authenticated())
    if current_user.is_authenticated():
        return redirect(url_for('menu'))
    elif get_trainer():
        return redirect(url_for('login'))
    else:
        return redirect(url_for('config'))

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/menu')
@login_required
def menu():
     return render_template('menu.html')
