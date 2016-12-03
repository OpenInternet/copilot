from flask.ext.wtf import Form

# Import Form elements
from wtforms import PasswordField, TextField, SelectField, FieldList, FormField, RadioField, HiddenField

# Import Form validators
from wtforms.validators import Required, Length, EqualTo, ValidationError, Optional, Regexp
from copilot.models.trainer import Trainer
from copilot.models.config import get_valid_actions, get_valid_targets
from copilot.utils.file_sys import get_usb_dirs

class LoginForm(Form):
    """ The login form"""
    password = PasswordField('Password', [Required(message='You must enter a password to enter.')])

class Config(Form):
    """ The initial configuration form.

    This page enables the trainer to setup a unique access point name and password
    for their training. By connecting to this access point, the trainees are then
    able to access the censorship environment.

    This page assists the user in setting up the trainer password or admin password
    for Co-Pilot so they are able to access the trainer interface.

    https://github.com/OpenInternet/co-pilot/wiki/User-Interface-Elements#initial-setup
    """
    ap_name = TextField('Trainee Access Point Name', validators=[
        Required(message='You must change the access point name.'),
        Length(min=1, max=31),
        Regexp("^[^\s]*$", message="AP Name cannot contain any spaces or tabs.")])
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
    """ Checks if a supplied field matches the current password.

    This function is a custom validator for checking if the current
    administrative password matches the supplied password.

    See: http://wtforms.simplecodes.com/docs/0.6/validators.html

    Args:
        form (WTForm - form): The full config form object.
        field (WTForm - field): The old password field to evaluate.
    """
    trainer = Trainer.query.get(1)
    if not trainer.is_correct_password(field.data):
        raise ValidationError('You did not enter your old password correctly. Please try again.')

class AdminConfig(Config):
    """ The admin configuration form.

    The admin configuration page allows the trainer to change the access point name
    and password, as well as the trainer password.

    https://github.com/OpenInternet/co-pilot/wiki/User-Interface-Elements#admin-configuration
    """
    old_password = PasswordField('Enter your current password to change these values.', validators=[
        Required(message='You must enter your current password to change any values.'),
        check_old_password])
    ap_name = TextField('Trainee Access Point Name', validators=[
        Optional(),
        Length(min=1, max=31),
        Regexp("^[^\s]*$", message="AP Name cannot contain any spaces or tabs.")])
    ap_password = PasswordField('Access Point Password', validators=[
        Optional(),
        Length(min=8, max=63),
        EqualTo('confirm_ap_pass', message='Passwords must match')])
    confirm_ap_pass = PasswordField('Repeat Access Point Password')
    password = PasswordField('Trainer Administration Password', validators=[
        Optional(),
        Length(min=3, max=31),
        EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Trainer Administration Password')

class RuleField(Form):
    """ A single rule object field

    This form is used within a field list in the profile form
    to represent each specific rule field.

    The possible rule "actions" and "targets" are pre-determined
    through a query to get_valid_actions. In the future these
    should be


    See the glossary for the difference between a rule and a
    profile. https://github.com/OpenInternet/co-pilot/wiki/Glossary
    """
    action = SelectField("Action", choices=zip(get_valid_actions(),
                                               get_valid_actions()))
    target = SelectField("Target", choices=zip(get_valid_targets(), get_valid_targets()))
    sub_target = TextField("Sub-Target")
    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(RuleField, self).__init__(*args, **kwargs)

class ProfileForm(Form):
    """ UNUSED profile configuration form

    TODO Remove this function or replace NewProfileForm
    with it and change calls to point to it instead.
    https://github.com/OpenInternet/co-pilot/issues/111
    """
    prof_name = TextField('Profile Name', default="new")
    rules = FieldList(FormField(RuleField))

class NewProfileForm(Form):
    """ The profile configuration form"""
    prof_name = TextField('Profile Name', default="new")
    rules = FieldList(FormField(RuleField))
