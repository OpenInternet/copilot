import os, random
from flask import Flask
from blockpage import blockpage
from flask import render_template


@blockpage.route('/', defaults={'path': ''})
@blockpage.route('/<path:path>')
def catch_all(path):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    image = random.choice(os.listdir(os.path.join(BASE_DIR, "static/images/dns/")))
    return render_template('blockpage.html', image="images/dns/{0}".format(image))

