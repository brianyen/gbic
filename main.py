from jinja2 import Template
import json
import os
import urllib
import datetime

def render(url):    
    out_dir = urllib.parse.quote_plus(url)
    out_dir = out_dir.replace("%", "-")
    stream = os.popen('python3 converter.py ' + url + ' ' + out_dir + ' ""')
    output = stream.read()

    slides = []
    i = 0
    while True:
        try:
            print("trying clip " + str(i))
            with open(out_dir + '/clip-' + "{:03d}".format(i) +'/slides.json') as f:
                data = f.read()
        except FileNotFoundError:
            break

        slides = slides + json.loads(data)
        i = i + 1
        
    try: 
        with open(out_dir + '/errors.txt') as f:
            errors =  f.read()
            print(errors)
    except FileNotFoundError:
        errors = ""   

    try:
        with open(out_dir + '/vid.info.json') as f:
            info = f.read()

        metadata = json.loads(info)
    except FileNotFoundError:
        metadata = {
            "fulltitle": "",
            "uploader": "",
            "duration": 0,
            "description": ""
        }

    with open('html.tmpl') as q:
        html = q.read()

    t = Template(html)

    return t.render(slides=slides, url=url, errors=errors, out_dir=out_dir, title=metadata["fulltitle"], creator=metadata["uploader"], duration=datetime.timedelta(seconds=metadata["duration"]), description=metadata["description"])
 
def convert_url(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    if request.args and 'url' in request.args:
        return render(request.args.get('url'))
    else:
        return "nothing"

def hello(request):
    return "Hello World!"