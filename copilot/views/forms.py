from flask.ext.wtf import Form

# Import Form elements
from wtforms import PasswordField, TextField

# Import Form validators
from wtforms.validators import Required, Length, EqualTo, ValidationError, Optional
from copilot.models import Trainer

# Define the login form
class LoginForm(Form):
    password = PasswordField('Password', [Required(message='You must enter a password to enter.')])

#Define the admin configuration form
class InitialConfig(Form):
    ap_name = TextField('Trainee Access Point Name', validators=[
        Required(message='You must change the access point name.'),
        Length(min=1, max=31)])
    ap_password = PasswordField('Access Point Password', validators=[
        Required(message='You must change the access point password.'),
        Length(min=8, max=63),
        EqualTo('confirm_ap_pass', message='Passwords must match')])
    confirm_ap_pass = PasswordField('Repeat Access Point Password')
    password = PasswordField('Trainer Administration Password', validators=[
        Required(message='You must create a trainer password.'),
        EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Trainer Administration Password')

def check_old_password(form, field):
    trainer = Trainer.query.get(1)
    if not trainer.is_correct_password(field.data):
        raise ValidationError('You did not enter your old password correctly. Please try again.')

#Define the admin configuration form
class AdminConfig(Form):
    old_password = PasswordField('Enter your current password to change these values.', validators=[
        Required(message='You must enter your current password to change any values.'),
        check_old_password])
    ap_name = TextField('Trainee Access Point Name', validators=[
        Optional(),
        Length(min=1, max=31)])
    ap_password = PasswordField('Access Point Password', validators=[
        Optional(),
        Length(min=8, max=63),
        EqualTo('confirm_ap_pass', message='Passwords must match')])
    confirm_ap_pass = PasswordField('Repeat Access Point Password')
    password = PasswordField('Trainer Administration Password', validators=[
        Optional(),
        EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Trainer Administration Password')

