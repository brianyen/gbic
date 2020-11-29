import os
import tempfile
import time
import shutil

def main(url):
    if verify_url(url):
        temp_dir = tempfile.TemporaryDirectory()
        print(temp_dir.name)
        return convert(url, temp_dir)
    else:
        return

def convert(url, temp_dir):
    stream = os.popen('../.././youtube-dl -o "' + temp_dir.name + '/vid.mp4" -f mp4 ' + url)
    output = stream.read()
    time.sleep(500)
    return output


def verify_url(url):
    return True

main("https://www.youtube.com/watch?v=gDqLFijKsfw")