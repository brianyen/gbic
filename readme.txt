personal NOTE: pip install = py -m pip install

IGNORE: py server.py > output.html (in gbic folder) to update

PUSHING FILES TO GOOGLE CLOUD STORAGE:
	(in google cloud shell)
	gsutil cp [location] gs://[bucket name]/
	ex:
		gsutil cp index.html gs://gbic/

personal NOTE: cd .. => go up by a directory

PUSHING FUNCTIONS TO GOOGLE CLOUD FUNCTIONS:
	(in google cloud shell)
	gcloud functions deploy convert_url --runtime python38 --trigger-http --allow-unauthenticated

personal NOTE:
	py -m venv env

SETTING UP LOCAL HOST:

	NOTE: two separate command shells
	NOTE: be in correct directory

	1.
	.\env\Scripts\activate ((in both shells))

	2.
	functions-framework --target convert_url --debug
		NOTE: need to install functions-framework if haven't yet

	3. 
	py -m http.server
		NOTE: in 2nd shell

	NOTE:
	^gbic-ajob1.html in localhost:8000
	^main.py in localhost:8080