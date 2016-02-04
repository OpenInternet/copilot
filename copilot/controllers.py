from flask import flash

#stat logging
import logging
log = logging.getLogger(__name__)

def flash_errors(form):
    """ Deliver error notifications from a form to a user.

    Iterates through all the errors in a form and creates
    flash text for those errors.

    See: http://flask.pocoo.org/snippets/12/

    Args:
        form (WTForm): The WTForm which encountered errors.
    """
    log.debug("Adding errors to flash.")
    for field, errors in form.errors.items():
        for error in errors:
            field_name = getattr(form, field).label.text
            log.debug("Error {0} added to field {1} in flash".format(
                field_name, error))
            flash(u"Error in the %s field - %s" % (
                field_name, error ), "error")
