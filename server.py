from jinja2 import Template
import json

with open('data.json') as f:
    data = f.read()

slides = json.loads(data)


with open('html.tmpl') as q:
    html = q.read()

	
h = html

t = Template(h)

print(t.render(slides=slides))
