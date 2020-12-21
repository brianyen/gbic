
from jinja2 import Template
import json

#with open('data.json') as f:
#	info_json = f.read()
#info_dict = json.loads(f)

#with open('data.json') as f:
#    info_json = f.read()
#info_dict = json.loads(info_json)

class text11:
	ts = "00:00"
	text = "1-1"

class text12:
	ts = "00:01"
	text = "1-2"

class text13:
	ts = "00:01.1"
	text = "1-3"

class text14:
	ts = "00:01.2"
	text = "1-4"

class text15:
	ts = "00:01.3"
	text = "1-5"

class text16:
	ts = "00:01.4"
	text = "1-6"

class text17:
	ts = "00:01.5"
	text = "1-7"

class text18:
	ts = "00:01.6"
	text = "1-8"

class text19:
	ts = "00:01.7"
	text = "1-9"

class text110:
	ts = "00:01.8"
	text = "1-10"


class text21:
	ts = "00:02"
	text = "2-1"

class text22:
	ts = "00:03"
	text = "2-2"

class text31:
	ts = "00:04"
	text = "3-1"

class text32:
	ts = "00:05"
	text = "3-2"

	
class slide1:
	img = "https://user-images.githubusercontent.com/194400/49531010-48dad180-f8b1-11e8-8d89-1e61320e1d82.png"
	text = [text11, text12, text13, text14, text15, text16, text17, text18, text19, text110]
	
class slide2:
	img = "https://user-images.githubusercontent.com/194400/49531010-48dad180-f8b1-11e8-8d89-1e61320e1d82.png"
	text = [text21, text22]
	
class slide3:
	img = "https://user-images.githubusercontent.com/194400/49531010-48dad180-f8b1-11e8-8d89-1e61320e1d82.png"
	text = [text31, text32]
	
slides = [slide1, slide2, slide3]



def paragraph(slide):
	i = ""
	for line in slide.text:
		i = i + "<p class='paragraph'>" + line.ts + ": " + line.text + "</p>"
	return i	

def groups(slides):
	v = ""
	for slide in slides:
		v = v + """<div class="group">
				<div class="column">
					<img class="slide" src=""" + slide.img + """ alt="placeholder image">
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

print(t.render(a="https://user-images.githubusercontent.com/194400/49531010-48dad180-f8b1-11e8-8d89-1e61320e1d82.png", insides=groups(slides)))