import os
import tempfile
import time
import shutil
import json
import math
import datetime
import sys
from google.cloud import storage

clip_length = 300.0
max_vid_length = 7200

#download_url = sys.argv[1]
out_dir = "test1"#sys.argv[2]
ytdl_prefix = ""#sys.argv[3

print('storage client')
gcs = storage.Client()
bucket = gcs.get_bucket('www.tubeslides.net')
print('storage client done')

#long video
#download_url = "https://www.youtube.com/watch?v=R44tKAPpKOM"

#short video
#download_url = "https://www.youtube.com/watch?v=4rA9E2FuLkU"
"""
gcs_client = storage.Client(project='gbic')
bucket = gcs_client.get_bucket('www.tubeslides.net')
blob = bucket.blob('v/' + out_dir)

blob.upload_from_string('', content_type='application/x-www-form-urlencoded;charset=UTF-8')
"""

##############################################################

def raiseError(message, temp_dir, out_dir):
    file = open(temp_dir.name + '/error.txt', "w")
    file.write(message)
    file.close()
    upload('error.txt', temp_dir, out_dir)
    sys.exit()

def main(url, out):
    temp_dir = tempfile.TemporaryDirectory()
    #out_dir = temp_dir.name
    print(temp_dir.name)
    out_dir = out
    print('getting vid info')
    get_video_info(url, temp_dir, out_dir)
    print('vid info get')

    print('getting video duration')
    duration = get_video_duration(url, temp_dir)
    verify_video_length(duration, temp_dir, out_dir)
    print('duration:' + str(duration))

    print('getting subtitles')
    instances = math.floor(duration / clip_length) + 1
    get_subtitles(url, temp_dir)
    subtitles = get_subtitles_with_ts(temp_dir)
    print('subtitles get')

    #Change temp_dir.name to output directory (video ID)
    file = open(temp_dir.name + '/subtitles.json', 'w')
    file.write(str(subtitles))
    file.close()
    upload('subtitles.json', temp_dir, out_dir)

    for i in range(instances):
        directory = 'clip-' + str(i).zfill(3)
        #Change temp_dir.name to output directory (video ID)
        path = os.path.join(temp_dir.name, directory)
        os.makedirs(path, exist_ok=True)
        convert_range_to_mp4(url, i, temp_dir)
        frames, fixed_timestamps = get_iframes(i, path, temp_dir, out_dir)
        slides_json = construct_json_file(i, fixed_timestamps, frames, subtitles)

        file = open(path + '/slides.json', 'w')
        file.write(slides_json)
        file.close()
        upload(directory + '/slides.json', temp_dir, out_dir)
    #Change temp_dir.name to output directory (video ID)
    file = open(temp_dir.name + '/done.txt', "x")
    file.close()
    upload('done.txt', temp_dir, out_dir)
    #convert_subtitles_to_transcript(subtitles)"""

def get_video_duration(url, temp_dir):
    with open(temp_dir.name + '/vid.info.json', 'r') as f:
        info = f.read()
    info_dict = json.loads(info)
    duration = info_dict.get("duration")
    return int(duration)

def get_video_info(url, temp_dir, out_dir):
    stream = os.popen(ytdl_prefix + 'youtube-dlc -o "' + temp_dir.name + '/vid" --write-info-json --skip-download ' + url)
    output = stream.read()
    upload('vid.info.json', temp_dir, out_dir)
    return output

def get_subtitles(url, temp_dir):
	stream = os.popen(ytdl_prefix + 'youtube-dlc -o "' + temp_dir.name + '/subs" --write-auto-sub --sub-format json3 --skip-download ' + url)
	output = stream.read()
	return output

def convert_range_to_mp4(url, instance, temp_dir):
    print("start downloading vid " + str(instance))
    start_time = clip_length * instance
    stream = os.popen('ffmpeg -ss ' + str(start_time) + ' -i $(' + ytdl_prefix + 'youtube-dlc -f 22 -g ' + url + ') -acodec copy -vcodec copy -t ' + str(clip_length) + ' ' + temp_dir.name + '/vid' + str(instance) + '.mp4')
    output = stream.read()
    print("finished downloading vid")
    return output

def get_iframes(instance, path, temp_dir, out_dir):
    #change min_frame_diff based on video runtime
    print('getting timestamps')
    timestamps = get_iframes_ts(instance, temp_dir)
    print(timestamps)

    min_frame_diff = 5
    last_ts = -math.inf
    frames = []
    fixed_timestamps = []
    for ts in timestamps:
        if ts - last_ts < min_frame_diff:
            continue
        hms_ts = convert_s_to_hms(round(ts))
        #make ffmpeg output "output.png" and rename it afterwards
        stream = os.popen('ffmpeg -ss ' + str(ts - (instance * clip_length)) + ' -i ' + temp_dir.name + '/vid' + str(instance) + '.mp4 -c:v png -frames:v 1 "' + path + '/slide-' + hms_ts + '.png"')
        while stream.read() != '':
            pass
        upload('clip-' + str(instance).zfill(3) + '/slide-' + hms_ts + '.png', temp_dir, out_dir)

        frames.append('clip-' + str(instance).zfill(3) + '/slide-' + hms_ts + '.png')
        fixed_timestamps.append(ts)
        last_ts = ts
    return frames, fixed_timestamps

def get_iframes_ts(instance, temp_dir):
    stream = os.popen('ffprobe -show_frames -of json -f lavfi "movie=' + temp_dir.name + '/vid' + str(instance) + '.mp4,select=gt(scene\\,0.1)"')
    output = stream.read()
    metadata = output[output.index("{"):]
    metadata_dict = json.loads(metadata)
    timestamps = []
    start_time = instance * clip_length
    timestamps.append(start_time)

    for frame in metadata_dict['frames']:
        timestamps.append(start_time + float(frame.get('best_effort_timestamp_time')))
    return timestamps

def get_subtitles_with_ts(temp_dir):
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
    start_time = instance * clip_length
    for i in range(0, num_frames):
        print(frames[i])
        time_rounded = round(timestamps[i])
        text_dict = []
        while current_line_ts < timestamps[i + 1] and line_num < len(subtitles) and current_line_ts < start_time + clip_length:
            line_timestamp = subtitles[line_num]['timestamp']
            if line_timestamp > start_time and line_timestamp < start_time + clip_length:
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
        print(iframe)
        converted_dict.append(iframe)
    return json.dumps(converted_dict, indent=4)

def verify_video_length(duration, temp_dir, out_dir):
    if duration > max_vid_length:
        raiseError("Video too long! Can only process videos shorter than 2 hours.", temp_dir, out_dir)

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

def upload(file, temp_dir, out_dir):
    # Create a new blob and upload the file's content.
    blob = bucket.blob('v/' + out_dir + '/' + file)

    print('uploading ' + temp_dir.name + '/' + file + ' to ' + out_dir)
    blob.upload_from_filename(temp_dir.name + '/' + file)
    print('success! uploaded ' + temp_dir.name + '/' + file)

    """
    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )
    """
    # The public URL can be used to directly access the uploaded file via HTTP.
    return blob.public_url

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

#main(download_url)
