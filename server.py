
from jinja2 import Template
import json

with open('data.json') as f:
    info_json = f.read()
info_dict = json.loads(info_json)


def paragraph(slide):
	i = ""
	for line in slide["text"]:
		i = i + "<p class='paragraph'>" + line["ts"] + ": " + line["text"] + "</p>"
	return i	

def groups(slides):
	v = ""
	for slide in slides:
		v = v + """<div class="group">
				<div class="column">
					<img class="slide" src=""" + slide["png"] + """ alt="placeholder image">
				</div>
				<div class="column">
					""" + paragraph(slide) + """
				</div>
			</div>"""
	return v
	

h = """<!DOCTYPE html>
<html>
<body id="body">
<div id="title">
	<h1>gbic</h1>
</div>
	
<div id="search">
	<input id="input"></input>
	<button onClick = "run()">Go</button>
	
	<div class="bar"></div>
</div>

<div id="content">
	{{ insides }}
</div>

<script>
var inputEl = document.getElementById("input")
var paragraphEl = document.getElementById("p1")


function run() {
	paragraphEl.innerHTML = inputEl.value
}

</script>

</body>
<style>
#body {
	margin: 0px;
}
#title {
	text-align: center;
	font-family: "Lucida Sans Unicode", "Lucida Grande", sans-serif;
	padding: 1px;
	font-size: 40px;
	background-color: rgb(185, 185, 255);
}
#search {
	text-align: right;
	margin: 20px;
}
#input {
	width: 250px;
}
.bar {
	border-top: 3px solid rgb(200, 200, 200);
	padding: 0px;
	margin: 50px;
	height: 0px;
}
.group {
	padding-bottom: 10px;
	display: flex;
}
div.column {
	width: 50%;
}
.slide {
	margin: 5%;
	width: 90%;
	position: sticky;
	top: 20px;
}
.paragraph {
	margin: 5%;
	font-family: "Lucida Sans Unicode", "Lucida Grande", sans-serif;
	width: 90%;
	word-wrap: break-word;
	overflow-x: hidden;
}
</style>
</html>"""

t = Template(h)

print(t.render(a="https://user-images.githubusercontent.com/194400/49531010-48dad180-f8b1-11e8-8d89-1e61320e1d82.png", insides=groups(info_dict)))
