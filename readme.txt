pip install = py -m pip install
-------

py server.py > output.html (in gbic folder) to update

(in google cloud shell)
	gsutil cp [location] gs://[bucket name]/ => pushing files into google cloud storage
	ex:
		gsutil cp gbic-ajob1.html gs://gbic/

cd .. => go up by a directory

(in google cloud shell)
	gcloud functions deploy hello_world --runtime python38 --trigger-http --allow-unauthenticated

py -m venv env

		setting up local host servers

(all within the correct directory)

1.
	.\env\Scripts\activate ((in both shells))

2.
	functions-framework --target convert_url --debug

3. 
	py -m http.server

(^gbic-ajob1.html in localhost:8000)
(^main.py in localhost:8080)