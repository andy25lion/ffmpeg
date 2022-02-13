from blinkpy import blinkpy
import datetime
import time
import os
import json
import glob

configPath = os.getenv('CONFIG_PATH')
streamName = os.getenv('STREAM')
with open(configPath) as json_file:
  APP_CONFIG = json.load(json_file)

STREAM_CONFIG = {}
for stream in APP_CONFIG['streams']:
  if stream['name'] == streamName:
    STREAM_CONFIG = stream
    break

username = STREAM_CONFIG['blink']['username']
password = STREAM_CONFIG['blink']['password']
authToken = STREAM_CONFIG['blink']['authToken']
downloadPath = os.path.join(APP_CONFIG['storagePath'], STREAM_CONFIG['name'], 'live')
archivePath  = os.path.join(APP_CONFIG['storagePath'], STREAM_CONFIG['name'], 'archive')
if not os.path.exists(downloadPath):
  os.makedirs(downloadPath)  
if not os.path.exists(archivePath):
  os.makedirs(archivePath)  
playlistFile = os.path.join(downloadPath, STREAM_CONFIG['livePlaylistName'])

blink = blinkpy.Blink()
auth = blinkpy.Auth({'username': username, 'password': password }, no_prompt=True)
blink.auth = auth
blink.start()

auth.send_auth_key(blink, authToken)
blink.setup_post_verify()

for name, camera in blink.cameras.items():
  print(name)                   # Name of the camera
  print(camera.attributes)      # Print available attributes of camera

camera = blink.cameras[STREAM_CONFIG['blink_cam']]
# blink.refresh(force_cache=True)  # force a cache update USE WITH CAUTION

# camera.image_from_cache.raw  # bytes-like image object (jpg)
# camera.image_to_file('/Users/andrei.csoric/Downloads/image.jpg')

# camera.snap_picture()       # Take a new picture with the camera
# blink.refresh()             # Get new information from server
# camera.image_to_file('/Users/andrei.csoric/Downloads/image2.jpg')

os.chdir(downloadPath)
while(True):
  blink.refresh() 
  since = datetime.datetime.now() - datetime.timedelta(minutes=2)
  sinceStr = since.strftime("%Y/%m/%d %H:%M")
  print('Getting from: ' + sinceStr)
  blink.download_videos('.', since=sinceStr)
  sortedFiles = sorted(glob.glob('*.mp4'))
  f = open(STREAM_CONFIG['livePlaylistName'], 'w')
  for file in sortedFiles:
    f.write(file+',0,0\n')
  f.close()

  if len(sortedFiles) > 5:
    if STREAM_CONFIG['archiveEnable']:
      os.rename(sortedFiles[0], os.path.join('../archive', sortedFiles[0]))
    else:
      os.remove(sortedFiles[0])
  time.sleep(2)
