from flask.ext.wtf import Form

# Import Form elements
from wtforms import PasswordField, TextField, SelectField, FieldList, FormField, RadioField, HiddenField

# Import Form validators
from wtforms.validators import Required, Length, EqualTo, ValidationError, Optional
from copilot.models.trainer import Trainer
from copilot.models.config import get_valid_actions, get_valid_targets
from copilot.utils.file_sys import get_usb_dirs

# Define the login form
class LoginForm(Form):
    password = PasswordField('Password', [Required(message='You must enter a password to enter.')])

#Define the admin configuration form
class Config(Form):
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
        Length(min=3, max=31),
        EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Trainer Administration Password')

def check_old_password(form, field):
    trainer = Trainer.query.get(1)
    if not trainer.is_correct_password(field.data):
        raise ValidationError('You did not enter your old password correctly. Please try again.')

class AdminConfig(Config):
    old_password = PasswordField('Enter your current password to change these values.', validators=[
        Required(message='You must enter your current password to change any values.'),
        check_old_password])

# #Define the admin configuration form
# class InitialConfig(Form):
#     ap_name = TextField('Trainee Access Point Name', validators=[
#         Required(message='You must change the access point name.'),
#         Length(min=1, max=31)])
#     ap_password = PasswordField('Access Point Password', validators=[
#         Required(message='You must change the access point password.'),
#         Length(min=8, max=63),
#         EqualTo('confirm_ap_pass', message='Passwords must match')])
#     confirm_ap_pass = PasswordField('Repeat Access Point Password')
#     password = PasswordField('Trainer Administration Password', validators=[
#         Required(message='You must create a trainer password.'),
#         EqualTo('confirm', message='Passwords must match')])
#     confirm = PasswordField('Repeat Trainer Administration Password')

# #Define the admin configuration form
# class AdminConfig(Form):
#     old_password = PasswordField('Enter your current password to change these values.', validators=[
#         Required(message='You must enter your current password to change any values.'),
#         check_old_password])
#     ap_name = TextField('Trainee Access Point Name', validators=[
#         Optional(),
#         Length(min=1, max=31)])
#     ap_password = PasswordField('Access Point Password', validators=[
#         Optional(),
#         Length(min=8, max=63),
#         EqualTo('confirm_ap_pass', message='Passwords must match')])
#     confirm_ap_pass = PasswordField('Repeat Access Point Password')
#     password = PasswordField('Trainer Administration Password', validators=[
#         Optional(),
#         EqualTo('confirm', message='Passwords must match')])
#     confirm = PasswordField('Repeat Trainer Administration Password')

class RuleField(Form):
    action = SelectField("Action", choices=zip(get_valid_actions(), get_valid_actions()), default="block")
    target = SelectField("Target", choices=zip(get_valid_targets(), get_valid_targets()), default="dns")
    sub_target = TextField("Sub-Target", default="")
    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(RuleField, self).__init__(*args, **kwargs)

class ProfileForm(Form):
    rules = FieldList(FormField(RuleField))

class NewProfileForm(Form):
    prof_name = TextField('Profile Name', default="new")
    rules = FieldList(FormField(RuleField))

class SaveProfileField(Form):
    prof_name = HiddenField('Profile Name', default="new")
    location = RadioField("Save Location", choices=(zip(get_usb_dirs() + ["Co-Pilot"], get_usb_dirs() + ["Co-Pilot"])), default="Co-Pilot")
