import os
import tempfile
import time
import shutil
import json

def main(url):
    if verify_url(url):
        temp_dir = tempfile.TemporaryDirectory()
        print(temp_dir.name)
        convert_to_mp4(url, temp_dir)
        timestamps = get_iframes_ts()
        return 
    else:
        return

def convert_to_mp4(url, temp_dir):
    #downloads video mp4 for ffmpeg
    stream = os.popen('../.././youtube-dlc -o "' + temp_dir.name + '/vid.mp4" --write-auto-sub --sub-format json3 -f mp4 ' + url)
    output = stream.read()
    with open(temp_dir.name + '/vid.en.json3', 'r') as f:
        data = f.read()
    print('---------')
    print(data)
    return output

def get_iframes_ts():
    stream = os.popen('ffprobe -show_frames -of json -f lavfi "movie=test-iframes/radix.mp4,select=gt(scene\\,0.1)"')
    output = stream.read()
    metadata = output[output.index("{"):]
    metadata_dict = json.loads(metadata)
    timestamps = []

    for frame in metadata_dict['frames']:
        timestamps.append(float(frame.get('best_effort_timestamp_time')))
    return timestamps

def verify_url(url):
    return True

main("https://www.youtube.com/watch?v=gDqLFijKsfw")