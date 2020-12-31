from jinja2 import Template
import json

def render(url):
    with open(url + '/clip-000/slides.json') as f:
        data = f.read()

    slides = json.loads(data)

    with open('html.tmpl') as q:
        html = q.read()

    t = Template(html)

    return t.render(slides=slides, url=url)
 
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
        print("hi")
        return render(request.args.get('url'))
    else:
        return "nothing"