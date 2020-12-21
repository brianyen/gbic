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
        subtitles = get_subtitles_with_ts(temp_dir)
        return 
    else:
        return

def convert_to_mp4(url, temp_dir):
    #downloads video mp4 for ffmpeg
    stream = os.popen('../.././youtube-dlc -o "' + temp_dir.name + '/vid.mp4" --write-auto-sub --sub-format json3 -f mp4 ' + url)
    output = stream.read()
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

def get_subtitles_with_ts(temp_dir):
    with open(temp_dir.name + '/vid.en.json3', 'r') as f:
        caption_json = f.read()
    caption_dict = json.loads(caption_json)

    captions_with_ts = []
    for event in caption_dict['events']:
        sentence = ""
        if "segs" in event:
            for word in event['segs']:
                sentence = sentence + word.get('utf8')
        line = {
            "timestamp": event.get('tStartMs'),
            "sentence": sentence
        }
        captions_with_ts.append(line)
    print('---------')
    print(captions_with_ts)

def verify_url(url):
    return True

main("https://www.youtube.com/watch?v=gDqLFijKsfw")