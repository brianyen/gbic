from jinja2 import Template
import json

def render(url):    
    slides = []
    i = 0
    while True:
        try:
            print("trying clip " + str(i))
            with open(url + '/clip-' + "{:03d}".format(i) +'/slides.json') as f:
                data = f.read()
        except FileNotFoundError:
            break

        slides = slides + json.loads(data)
        i = i + 1
        
    try: 
        with open(url + '/errors.txt') as f:
            errors =  f.read()
            print(errors)
    except FileNotFoundError:
        errors = ""   

    with open('html.tmpl') as q:
        html = q.read()

    t = Template(html)

    return t.render(slides=slides, url=url, errors=errors)
 
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