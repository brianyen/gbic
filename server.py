import flask
from flask import request, send_from_directory

import re
import urllib
import subprocess

progress = {}

app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.send_file('index.html')

@app.route('/view.html')
def view():
    return flask.send_file('view.html')
    
@app.route('/go', methods = ['POST'])
def go():
    print("request", request)
    url = str(request.form.get('url'))
    url_short = re.sub('^https?://', '', url)
    print("url_short", url_short)
    out_dir = urllib.parse.quote_plus(url_short)
    out_dir = out_dir.replace("%", "-")

    subprocess.Popen(['py', 'converter.py', url, out_dir])
    
    # spawn a child thread, which reads the stdout from converter.py
    # and then updates the global progress dict, like...
    #  progress[out_dir] = 130

    return flask.redirect('/view.html?out_dir=' + out_dir)

@app.route('/v/<path:p>')
def v(p):
    return send_from_directory('temp', p)

@app.route('/progress/<string:v>')
def progress(v):
    return progress[v]

app.run(host='0.0.0.0', port=81, debug=True)
