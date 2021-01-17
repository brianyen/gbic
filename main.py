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

# -------------------------------------------------------

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

# -------------------------------------------------------

def cookies_refresh(event, context):
    import os, http.cookiejar, urllib.request

    cj = http.cookiejar.MozillaCookieJar()

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    r = opener.open("https://www.youtube.com")

    print("cj", cj)

    cj.save("/tmp/cookies.txt")

    print("cj saved")

    gcs_client = storage.Client(project='gbic')
    bucket = gcs_client.get_bucket('www.tubeslides.net')
    blob = bucket.blob('cookies.txt')

    print("cookies.txt uploading")
    blob.upload_from_filename('/tmp/cookies.txt')

    print("cookies.txt uploaded")
