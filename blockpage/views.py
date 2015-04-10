import os, random
from flask import Flask
app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path>')
def catch_all(path):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    image = random.choice(os.listdir(os.path.join(BASE_DIR, "/static/images/dns/")))
    print(image)
    print("IT GOT HERE")
    return render_template('blockpage.html', image=image)
    
