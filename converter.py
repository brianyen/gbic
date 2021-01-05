import os
import tempfile
import time
import shutil
import json
import math
import datetime
import sys
from google.cloud import storage

download_url = sys.argv[1]
out_dir = sys.argv[2]
ytdl_prefix = sys.argv[3]

#long video
#download_url = "https://www.youtube.com/watch?v=R44tKAPpKOM"

#short video
#download_url = "https://www.youtube.com/watch?v=4rA9E2FuLkU"

gcs_client = storage.Client(project='gbic')
bucket = gcs_client.get_bucket('www.tubeslides.net')
blob = bucket.blob('www.tubeslides.net/v/' + out_dir)

blob.upload_from_string('', content_type='application/x-www-form-urlencoded;charset=UTF-8')

temp_dir = tempfile.TemporaryDirectory()
#out_dir = temp_dir.name
print(temp_dir.name)

##############################################################

def raiseError(message):
    file = open(out_dir + '/error.txt', "w")
    file.write(message)
    file.close()
    sys.exit()

def main(url):
    duration = get_video_duration(url)
    verify_video_length(duration)
    print(duration)

    instances = math.floor(duration / 300) + 1
    get_subtitles(url)
    subtitles = get_subtitles_with_ts()

    get_video_info(url)

    #Change temp_dir.name to output directory (video ID)
    os.makedirs(out_dir, exist_ok=True)
    file = open(out_dir + '/subtitles.json', 'w')
    file.write(str(subtitles))
    file.close()

    for i in range(instances):
        directory = 'clip-' + str(i).zfill(3)
        #Change temp_dir.name to output directory (video ID)
        path = os.path.join(out_dir, directory)
        os.makedirs(path, exist_ok=True)
        convert_range_to_mp4(url, i)
        frames, fixed_timestamps = get_iframes(i, path)
        slides_json = construct_json_file(i, fixed_timestamps, frames, subtitles)
        print(slides_json)

        file = open(path + '/slides.json', 'w')
        file.write(slides_json)
        file.close()
    #Change temp_dir.name to output directory (video ID)
    file = open(out_dir + '/done.txt', "x")
    file.close()
    #convert_subtitles_to_transcript(subtitles)"""

def get_video_duration(url):
    stream = os.popen(ytdl_prefix + 'youtube-dlc --get-duration ' + url)
    output = stream.read()
    duration = get_sec(output)
    return duration

def get_video_info(url):
    stream = os.popen(ytdl_prefix + 'youtube-dlc -o "' + out_dir + '/vid" --write-info-json --skip-download ' + url)
    output = stream.read()
    return output

def get_subtitles(url):
	stream = os.popen(ytdl_prefix + 'youtube-dlc -o "' + temp_dir.name + '/subs" --write-auto-sub --sub-format json3 --skip-download ' + url)
	output = stream.read()
	return output

def convert_range_to_mp4(url, instance):
    start_time = 300 * instance
    stream = os.popen('ffmpeg -ss ' + str(start_time) + ' -i $(' + ytdl_prefix + 'youtube-dlc -f 22 -g ' + url + ') -acodec copy -vcodec copy -t 300 ' + temp_dir.name + '/vid' + str(instance) + '.mp4')
    output = stream.read()
    return output

def get_iframes(instance, path):
    #change min_frame_diff based on video runtime
    timestamps = get_iframes_ts(instance)

    min_frame_diff = 5
    last_ts = -math.inf
    frames = []
    fixed_timestamps = []
    for ts in timestamps:
        if ts - last_ts < min_frame_diff:
            continue
        hms_ts = convert_s_to_hms(round(ts))
        #make ffmpeg output "output.png" and rename it afterwards
        stream = os.popen('ffmpeg -ss ' + str(ts - (instance * 300)) + ' -i ' + temp_dir.name + '/vid' + str(instance) + '.mp4 -c:v png -frames:v 1 "' + path + '/slide-' + hms_ts + '.png"')
        os.system('ls ' + temp_dir.name)
        #os.rename(temp_dir.name + '/output.png', path + '/slide-' + hms_ts + '.png')
        os.system('ls ' + path)
       	for i in range (10):
       		print(" ")
        output = stream.read()
        frames.append('clip-' + str(instance).zfill(3) + '/slide-' + hms_ts + '.png')
        fixed_timestamps.append(ts)
        last_ts = ts
    return frames, fixed_timestamps

def get_iframes_ts(instance):
    stream = os.popen('ffprobe -show_frames -of json -f lavfi "movie=' + temp_dir.name + '/vid' + str(instance) + '.mp4,select=gt(scene\\,0.1)"')
    output = stream.read()
    metadata = output[output.index("{"):]
    metadata_dict = json.loads(metadata)
    timestamps = []
    start_time = instance * 300.0
    timestamps.append(start_time)

    for frame in metadata_dict['frames']:
        timestamps.append(start_time + float(frame.get('best_effort_timestamp_time')))
    return timestamps

def get_subtitles_with_ts():
    with open(temp_dir.name + '/subs.en.json3', 'r') as f:
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

def construct_json_file(instance, timestamps, frames, subtitles):
    num_frames = len(frames)
    timestamps.append(math.inf)
    converted_dict = []
    line_num = 0
    current_line_ts = 0
    start_time = instance * 300
    for i in range(0, num_frames):
        time_rounded = round(timestamps[i])
        text_dict = []
        while current_line_ts < timestamps[i + 1] and line_num < len(subtitles) and current_line_ts < start_time + 300:
            line_timestamp = subtitles[line_num]['timestamp']
            if line_timestamp > start_time:
                lines = {
                    "ts": convert_s_to_hms(round(line_timestamp)),
                    "text": subtitles[line_num]['sentence']
                }
                text_dict.append(lines)
            line_num += 1
            current_line_ts = line_timestamp

        iframe = {
            "ts": convert_s_to_hms(time_rounded),
            "png": frames[i],
            "text": text_dict
        }
        converted_dict.append(iframe)
    return json.dumps(converted_dict, indent=4)

def verify_video_length(duration):
    if duration > 7200:
        raiseError("Video too long! Can only process videos shorter than 2 hours.")

def convert_ms_to_s(x):
    return x / 1000.0

def convert_s_to_hms(x):
    date = str(datetime.timedelta(seconds=x))
    return date.replace(":", "-")

def get_sec(time_str):
    """Get Seconds from time."""
    count = 0;
    for i in time_str:
        if i == ':':
            count += 1
    if count == 0:
        return int(time_str)
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

def upload_to_bucket(blob_name, path_to_file, bucket_name):
    """ Upload data to a bucket"""

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json(
        'creds.json')

    #print(buckets = list(storage_client.list_buckets())

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(path_to_file)

    #returns a public url
    return blob.public_url

##############################################################

main(download_url)
