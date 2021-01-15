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

    return flask.redirect('https://www.tubeslides.net/view.html?out_dir=' + out_dir)