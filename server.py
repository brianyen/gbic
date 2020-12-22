from jinja2 import Template
import json

with open('data.json') as f:
    data = f.read()

slides = json.loads(data)


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

{% for slide in slides %}
    <div>
		<p class="paragraph" style="margin-top: 5px; margin-bottom: 5px">{{ slide.ts }}</p>
		<div class="group">
			<div class="column">
				<img class="slide" src="{{ slide.png }}" alt="placeholder image">
			</div>
			<div class="column">
				{% for line in slide.text %}
					<p class='paragraph'> {{ line.ts }} <br> {{ line.text }} </p>
				{% endfor %}
			</div>
		</div>
    </div>    
{% endfor %}

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

print(t.render(slides=slides))
