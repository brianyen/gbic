import os
import tempfile
import time
import shutil
import json
import math

def main(url):
    if verify_url(url):
        temp_dir = tempfile.TemporaryDirectory()
        print(temp_dir.name)
        convert_to_mp4(url, temp_dir)
        timestamps = get_iframes_ts(temp_dir)
        frames = get_iframes(temp_dir, timestamps)
        print(frames)
        subtitles = get_subtitles_with_ts(temp_dir)
        return 
    else:
        return

def convert_to_mp4(url, temp_dir):
    #downloads video mp4
    stream = os.popen('../.././youtube-dlc -o "' + temp_dir.name + '/vid.mp4" --write-auto-sub --sub-format json3 -f mp4 ' + url)
    output = stream.read()
    return output

def get_iframes(temp_dir, timestamps):
    min_frame_diff = 5
    last_ts = -math.inf
    frames = []
    for ts in timestamps:
        if ts - last_ts < min_frame_diff:
            continue
        stream = os.popen('ffmpeg -ss ' + str(ts) + ' -i ' + temp_dir.name + '/vid.mp4 -c:v png -frames:v 1 ' + temp_dir.name + '/frame-' + str(ts) + '.png')
        output = stream.read()
        frames.append('frame-' + str(ts) + '.png')
        last_ts = ts
    return frames

def get_iframes_ts(temp_dir):
    stream = os.popen('ffprobe -show_frames -of json -f lavfi "movie=test-iframes/radix.mp4,select=gt(scene\\,0.1)"')
    output = stream.read()
    metadata = output[output.index("{"):]
    metadata_dict = json.loads(metadata)
    timestamps = []
    timestamps.append(0.0)

    for frame in metadata_dict['frames']:
        timestamps.append(float(frame.get('best_effort_timestamp_time')))
    return timestamps

def get_subtitles_with_ts(temp_dir):
    with open(temp_dir.name + '/vid.en.json3', 'r') as f:
        subtitle_json = f.read()
    subtitle_dict = json.loads(subtitle_json)

    subtitles_with_ts = []
    for event in subtitle_dict['events']:
        sentence = ""
        if "segs" in event:
            for word in event['segs']:
                sentence = sentence + word.get('utf8')
        line = {
            "timestamp": convert_ms_to_s(event.get('tStartMs')),
            "sentence": sentence
        }
        if line['sentence'] != '\n' and len(line['sentence']) > 0:
            subtitles_with_ts.append(line)
    return subtitles_with_ts

def verify_url(url):
    return True

def convert_ms_to_s(x):
    return x / 1000.0

main("https://www.youtube.com/watch?v=gDqLFijKsfw")