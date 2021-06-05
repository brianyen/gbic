# gbic first

The gbic project is here.

The google doc...

https://docs.google.com/document/d/1IhFaIB7Ra5CqwMpOKDzSog5JT2EmV-YC26nUo3UYTT8/edit?ts=5fc17230#

___

personal NOTE: pip install = py -m pip install

IGNORE: py server.py > output.html (in gbic folder) to update

PUSHING FILES TO GOOGLE CLOUD STORAGE:

	(in google cloud shell)
	gsutil cp [location] gs://[bucket name]/
	ex:
		gsutil cp index.html gs://www.tubeslides.net/
		gsutil cp view.html gs://www.tubeslides.net/

personal NOTE: cd .. => go up by a directory

PUSHING FUNCTIONS TO GOOGLE CLOUD FUNCTIONS:

	(in google cloud shell)
	gcloud functions deploy convert_url --runtime python38 --trigger-http --memory 2048MB --allow-unauthenticated

personal NOTE:

	py -m venv env

SETTING UP LOCAL HOST:

	NOTE: two separate command shells
	NOTE: be in correct directory

	1.
	.\env\Scripts\activate ((in both shells))
	
	pip3 install jinja2
	pip3 install -r requirements.txt

	2.
	functions-framework --target convert_url --debug
		NOTE: need to install functions-framework if haven't yet

	3. 
	py -m http.server
		NOTE: in 2nd shell

	NOTE:
	^index.html in localhost:8000
	^main.py in localhost:8080

CORS

	gsutil cors set CORS.json gs://www.tubeslides.net
	gsutil cors get gs://www.tubeslides.net
	
RUNNING converter_local.py

	python3 converter_local.py <Youtube URL> <OUTPUT DIRECTORY> <PREFIX TO ACCESS YOUTUBE-DL>
