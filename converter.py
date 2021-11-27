import os
import os.path
import tempfile
import time
import shutil
import json
import math
import datetime
import sys
import numpy as np
import cv2

clip_length = 300.0 #5 minutes
max_vid_length = 7200 #2 hours

ytdl_prefix = ""
host = 0

ytdl_cmd = "youtube-dl"

#long video
#download_url = "https://www.youtube.com/watch?v=R44tKAPpKOM"

#short video
#download_url = "https://www.youtube.com/watch?v=4rA9E2FuLkU"

##############################################################

def raiseError(message, temp_dir, out_dir):
    file = open(temp_dir + '/error.txt', "w")
    file.write(message)
    file.close()
    upload('error.txt', temp_dir, out_dir)
    sys.exit()

def main(url, out):
    if False:
        files = [f for f in os.listdir('./static') if f != 'cookies.txt']
        for f in files:
            if (os.path.isfile('./static/' + f)):
                os.remove('./static/' + f)
            else:
                shutil.rmtree('./static/' + f) 

    out_dir = out
#    temp_dir = tempfile.TemporaryDirectory().name
    temp_dir = "./temp/" + out_dir
    #out_dir = temp_dir
    print(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
#    get_cookies(temp_dir)

    print('getting vid info', url, temp_dir, out_dir)
    get_video_info(url, temp_dir, out_dir)
    print('vid info get')

    print('getting video duration')
    duration = get_video_duration(url, temp_dir)
    verify_video_length(duration, temp_dir, out_dir)
    print('duration:' + str(duration))

    print('getting subtitles')
    instances = math.floor(duration / clip_length) + 1
    get_subtitles(url, temp_dir, out_dir)
    subtitles = get_subtitles_with_ts(temp_dir)
    print('subtitles get')

    #Change temp_dir to output directory (video ID)
    file = open(temp_dir + '/subtitles.json', 'w')
    file.write(str(subtitles))
    file.close()
    upload('subtitles.json', temp_dir, out_dir)

    for i in range(instances):
        directory = 'clip-' + str(i).zfill(3)
        #Change temp_dir to output directory (video ID)
        path = os.path.join(temp_dir, directory)
        os.makedirs(path, exist_ok=True)
        convert_range_to_mp4(url, i, temp_dir, out_dir)
        frames, fixed_timestamps = get_iframes(i, duration, path, temp_dir, out_dir)
        slides_json = construct_json_file(i, fixed_timestamps, frames, subtitles)

        file = open(path + '/slides.json', 'w')
        file.write(slides_json)
        file.close()
        upload(directory + '/slides.json', temp_dir, out_dir)
    #Change temp_dir to output directory (video ID)
    file = open(temp_dir + '/done.txt', "x")
    file.close()
    upload('done.txt', temp_dir, out_dir)
    #convert_subtitles_to_transcript(subtitles)"""

def get_video_duration(url, temp_dir):
    with open(temp_dir + '/vid.info.json', 'r') as f:
        info = f.read()
    info_dict = json.loads(info)
    duration = info_dict.get("duration")
    return int(duration)

def get_video_info(url, temp_dir, out_dir):
    print("url", url)
    cmd = ytdl_prefix + ytdl_cmd + ' -o "' + temp_dir + \
        '/vid" --write-info-json --cookies ' + temp_dir + \
        '/cookies.txt --skip-download ' + url
    print("cmd_vid_info:", cmd)
    stream = os.popen(cmd)
    output = stream.read()
    if output == '':
        raiseError("Error getting video information.", temp_dir, out_dir)
    upload('vid.info.json', temp_dir, out_dir)
    return output

def get_subtitles(url, temp_dir, out_dir):
    cmd = ytdl_prefix + ytdl_cmd + ' -o "' + temp_dir + \
        '/subs" --write-auto-sub --write-sub --sub-format json3 --cookies ' + \
        temp_dir + '/cookies.txt --skip-download ' + url
    print("cmd_subs:", cmd)
    stream = os.popen(cmd)
    output = stream.read()
    if output == '':
        raiseError("Error getting video subtitles. Video may have no subtitles available.", temp_dir, out_dir)
    return output

def convert_range_to_mp4(url, instance, temp_dir, out_dir):
    print("start downloading vid " + str(instance))
    start_time = clip_length * instance
    full_url = str(os.popen(ytdl_prefix + ytdl_cmd + ' -f 22 -g --cookies ' + temp_dir + '/cookies.txt ' + url).read()).strip()
    print("full_url", full_url)
    cmd = 'ffmpeg -ss ' + str(start_time) + ' -i "' + full_url + '" -acodec copy -vcodec copy -t ' + str(clip_length) + \
        ' ' + temp_dir + '/vid' + str(instance) + '.mp4'
    print("cmd: " + cmd)
    stream = os.popen(cmd)
    output = stream.read()
    if output == '':
        raiseError("Error while processing video.", temp_dir, out_dir)
    print("finished downloading vid")
    return output

def get_iframes(instance, duration, path, temp_dir, out_dir):
    min_frame_diff = 5
    frames = []
    timestamps = []
    start_time = instance * clip_length

    #finds the length of the clip current instance is on
    total_instances = math.floor(duration / clip_length) + 1
    if instance < total_instances - 1:
        vid_length = clip_length
    else:
        vid_length = duration % clip_length
    print(vid_length)

    #downloads a png every second in the clip
    second = 0
    while second < vid_length:
        hms_ts = convert_s_to_hms(start_time + second)
        stream = os.popen('ffmpeg -loglevel quiet -ss ' + str(second) + ' -i ' + temp_dir + '/vid' + str(instance) + '.mp4 -s 720x480 -c:v png -frames:v 1 "' + path + '/slide-' + hms_ts + '.png"')
        output = stream.read()
        if output == '':
            raiseError("Error in finding key frames.", temp_dir, out_dir)
        second = second + 10
        print(second)

    #uploads and gathers info for first frame
    frame_name = '/slide-' + convert_s_to_hms(start_time) + '.png'
    frames.append('clip-' + str(instance).zfill(3) + frame_name)
    timestamps.append(start_time)
    upload('clip-' + str(instance).zfill(3) + frame_name, temp_dir, out_dir)

    #finds i-frames by comparing all the images and reporting differences
    previous_iframe = 0
    original = cv2.imread(path + frame_name)
    curr_frame = 10

    while curr_frame < vid_length:
        frame_name = '/slide-' + convert_s_to_hms(start_time + curr_frame) + '.png'
        contrast = cv2.imread(path + frame_name)
        if curr_frame - previous_iframe >= min_frame_diff:
            diff = mse(original, contrast)
            if diff > 1000.0:
                original = contrast
                previous_iframe = curr_frame
                upload('clip-' + str(instance).zfill(3) + frame_name, temp_dir, out_dir)
                timestamps.append(start_time + curr_frame)
                frames.append('clip-' + str(instance).zfill(3) + frame_name)
        curr_frame = curr_frame + 10

    print(timestamps)
    print(frames)
    return frames, timestamps

def get_subtitles_with_ts(temp_dir):
    with open(temp_dir + '/subs.en.json3', 'r') as f:
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
    count = 0
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

def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])

    return err

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
    return

def get_cookies(temp_dir):
    return

##############################################################

#main(download_url)

if __name__ == '__main__':
    url = sys.argv[1]
    out = sys.argv[2]
    print("start main")
    main(url, out)
    print("main done")
