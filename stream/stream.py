import subprocess
import shlex
import datetime
import os
import signal
import json

def write_log(str, file):
    file.write(str + '\n')
    # print(log_str)
    file.flush()

def new_sync(filename):
    ts = datetime.datetime.now()
    sync_file = open(filename, 'w+')
    log_str = '['+str(ts)+'] START'
    sync_file.write(log_str + '\n')
    print(log_str)
    return sync_file

def make_path(path):
    print(path)
    if not os.path.exists(path):
        os.makedirs(path)

if __name__ == "__main__":
    configPath = os.getenv('CONFIG_PATH')
    streamName = os.getenv('STREAM')
    with open(configPath) as json_file:
        APP_CONFIG = json.load(json_file)
    command = ''
    logFilename = 'log.log'

    
    for stream in APP_CONFIG['streams']:
        if stream['name'] == streamName:
            logFilename = os.path.join(APP_CONFIG['storagePath'], stream['name'], stream['name'] + '.log')
            streamDir = os.path.join(APP_CONFIG['storagePath'], stream['name'])
            make_path(streamDir)
            os.chdir(streamDir)
            make_path(os.path.dirname(stream['liveSegment']))
            make_path(os.path.dirname(stream['archiveSegment']))
            if stream['archiveEnable']:
                command = stream['ffmpeg']['base'] + ' ' + \
                    stream['ffmpeg']['liveArgs'].format(playlist_path=stream['livePlaylistName'], file_path=stream['liveSegment']) + ' ' + \
                    stream['ffmpeg']['archiveArgs'].format(playlist_path=stream['archivePlaylistName'], file_path=stream['archiveSegment'])
            else:
                command = stream['ffmpeg']['base'] + ' ' + \
                    stream['ffmpeg']['liveArgs'].format(playlist_path=stream['livePlaylistName'], file_path=stream['liveSegment'])
            break

    if not command == '':
        sync_file = new_sync(logFilename)
        print(command)
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            while True:
                output = process.stderr.readline().decode('utf8')
                # print(output)
                if output == '' and process.poll() is not None:
                    break
                if output:
                    if 'demuxer ->' in output:
                        # output = output.split('pkt_pts_time:')[1].split(' ')[0]
                        ts = datetime.datetime.now()
                        log_str = '['+str(ts)+'] PTS: ' + output.strip()
                        write_log(log_str, sync_file)
                    if 'Opening ' in output:
                        print(output)
                        ts = datetime.datetime.now()
                        log_str = '['+str(ts)+'] ' + output.strip()
                        write_log(log_str, sync_file)
            rc = process.poll()
        except KeyboardInterrupt:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)