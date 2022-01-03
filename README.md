# gbic first

The gbic project is here!

The google doc...

https://docs.google.com/document/d/1IhFaIB7Ra5CqwMpOKDzSog5JT2EmV-YC26nUo3UYTT8/edit?ts=5fc17230#

___
locally run:
	$ venv\Scripts\activate
	$ server.py

-download Python 3
-create venv
	$ py -m venv venv
-pip install modules (in venv)
	$ py -m pip install <MODULE NAME>
		" <flask>
		" <opencv-python>
		" <numpy>
		" <ffmpeg>
		" <regex>

	$ py -m pip install --upgrade youtube-dlc
		add to path

	https://www.gyan.dev/ffmpeg/builds/ download ffmpeg
		unzip in 'gbic' dir and copy "ffmpeg(.exe)" into 'gbic' dir

	ffmpeg.exe -> linux: https://gist.github.com/willmasters/382fe6caba44a4345a3de95d98d3aae5

	note: depending on OS might need to install libGL

Linking 'py' to 'python3' (for linux)
	$ cd
	$ cd /usr/bin/
	$ ln -s /usr/bin/python3 py

docker build -t hello-world .

Docker:
locally     $ docker push (name)
on ec2 instance -   $ docker pull (name)
					$ docker run -p 80:80 (name)