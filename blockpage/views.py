import os, random
from flask import Flask
from blockpage import blockpage
from flask import render_template


@blockpage.route('/', defaults={'path': ''})
@blockpage.route('/<path:path>')
def catch_all(path):
    """ A catch all route that redirects all requests to the blockpage."""
    return render_template('blockpage.html')
