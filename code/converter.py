import os
import tempfile
import time
import shutil
import json
import math
import datetime
import youtube_dl
from youtube_dl import YoutubeDL

def main(url):
    if verify_url(url):
        temp_dir = tempfile.TemporaryDirectory()
        real_url = get_real_url(url)
        duration = get_video_duration(url)
        instances = math.floor(duration / 300) + 1

        convert_to_mp4(url, temp_dir)
        initial_timestamps = get_iframes_ts(temp_dir, real_url)
        frames, fixed_timestamps = get_iframes(temp_dir, initial_timestamps)
        subtitles = get_subtitles_with_ts(temp_dir)
        frame_json = construct_json_file(fixed_timestamps, frames, subtitles)
        print(frame_json)
        #convert_subtitles_to_transcript(subtitles)
        return 
    else:
        temp_dir = tempfile.TemporaryDirectory()
        real_url = get_real_url(url)
        return

def get_video_duration(url):
    stream = os.popen('../.././youtube-dlc --get-duration ' + url)
    output = stream.read()
    duration = get_sec(output)
    return duration

def convert_range_to_mp4(url, instance_num, tempdir):
    start_time = 300 * instance_num
    stream = os.popen('ffmpeg -ss ' + start_time + ' -i $(../.././youtube-dlc -f 22 -g ' + url + ') -acodec copy -vcodec copy -t 300 output' + instance_num + '.mp4')
    output = stream.read()
    return output

def convert_to_mp4(url, temp_dir):
    #downloads video mp4
    stream = os.popen('../.././youtube-dlc -o "' + temp_dir.name + '/vid.mp4" --write-auto-sub --sub-format json3 -f mp4 ' + url)
    output = stream.read()
    return output

def get_iframes(temp_dir, timestamps):
    #change min_frame_diff based on video runtime
    min_frame_diff = 5
    last_ts = -math.inf
    frames = []
    fixed_timestamps = []
    for ts in timestamps:
        if ts - last_ts < min_frame_diff:
            continue
        stream = os.popen('ffmpeg -ss ' + str(ts) + ' -i ' + temp_dir.name + '/vid.mp4 -c:v png -frames:v 1 ' + temp_dir.name + '/frame-' + str(ts) + '.png')
        output = stream.read()
        frames.append('frame-' + str(ts) + '.png')
        fixed_timestamps.append(ts)
        last_ts = ts
    return frames, fixed_timestamps

def get_iframes_ts(temp_dir, url):
    stream = os.popen('ffprobe -show_frames -of json -f lavfi "movie=' + temp_dir.name + '/vid.mp4,select=gt(scene\\,0.1)"')
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

def construct_json_file(timestamps, frames, subtitles):
    num_frames = len(frames)
    timestamps.append(math.inf)
    converted_dict = []
    line_num = 0
    current_line_ts = 0
    for i in range(0, num_frames):
        time_rounded = round(timestamps[i])
        text_dict = []
        while current_line_ts < timestamps[i + 1] and line_num < len(subtitles):
            line_timestamp = subtitles[line_num]['timestamp']
            lines = {
                "ts": convert_s_to_hms(round(line_timestamp)),
                "text": subtitles[line_num]['sentence']
            }
            line_num += 1
            current_line_ts = line_timestamp
            text_dict.append(lines)

        iframe = {
            "ts": convert_s_to_hms(time_rounded),
            "png": frames[i],
            "text": text_dict
        }
        converted_dict.append(iframe)
    return json.dumps(converted_dict, indent=4)

def verify_url(url):
    return True

def convert_ms_to_s(x):
    return x / 1000.0

def convert_s_to_hms(x):
    return str(datetime.timedelta(seconds=x))

def get_sec(time_str):
    """Get Seconds from time."""
    count = 0;
    for i in time_str:
        if i == ':':
            count += 1
    if count == 0:
        return time_str
    if count == 1:
        m, s = time_str.split(':')
        return int(m) * 60 + int(s)
    else:
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)

##############################################################

def convert_subtitles_to_transcript(subtitles):
    transcript = subtitles[0]['sentence']
    for i in range(1, 5):
        transcript = transcript + " " + subtitles[i]['sentence']
    punctuated_transcript = add_punctuation(transcript)
    print(punctuated_transcript)
    return transcript

def add_punctuation(transcript):
    fastpunct = FastPunct('en')
    return fastpunct.punct([transcript], batch_size=32)
    #return fastpunct.punct([transcript], batch_size=32)

##############################################################

def get_real_url(url):
    stream = os.popen('../.././youtube-dlc -g "' + url + '"')
    output = stream.read()
    first_url = 'https'.join(output.split("https", 2)[:2])
    return first_url

##############################################################

download_url = "https://www.youtube.com/watch?v=4rA9E2FuLkU"
main(download_url)
