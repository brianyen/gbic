from jinja2 import Template
import json
import os
import urllib
import datetime
import converter
import base64
import re
import flask
from google.cloud import pubsub_v1

def render(url):    
    out_dir = urllib.parse.quote_plus(url)
    out_dir = out_dir.replace("%", "-")
    stream = os.popen('python3 converter.py ' + url + ' ' + out_dir + ' ""')
    output = stream.read()
    print(output)

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
 
def convert_url_old(request):
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

def alex(request):
    if request.args and 'url' in request.args:
        return converter.main(request.args.get('url'))
    else:
        return "nothing2"

def convert_url_sub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    data = base64.b64decode(event['data']).decode('utf-8')
    data_dict = json.loads(data)
    if data:
        return converter.main(data_dict.get("url"), data_dict.get("out_dir"))
    else:
        return "nothing3"

def convert_url(request):
    url = str(request.args.get('url'))
    url_short = re.sub('^https?://', '', url)

    out_dir = urllib.parse.quote_plus(url_short)
    out_dir = out_dir.replace("%", "-")

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path("decisive-plasma-299605", "convert_url")

    data = {
        "url": url,
        "out_dir": out_dir
    }
    data_json = json.dumps(data)

    publisher.publish(topic_path, data_json.encode("utf-8"))

    print(f"Published message to {topic_path}.")

    return flask.redirect('/view.html?out_dir=' + out_dir)