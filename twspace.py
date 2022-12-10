import os
import urllib.request
import re


base_url = 'https://prod-fastly-us-east-1.video.pscp.tv'
base_addon = '/Transcoding/v1/hls/'
space_id = input('space id = ')
end_masterurl = "/non_transcode/us-east-1/periscope-replay-direct-prod-us-east-1-public/audio-space/master_playlist.m3u8"
end_chunkurl = '/non_transcode/ap-northeast-1/periscope-replay-direct-prod-ap-northeast-1-public/audio-space/chunk'
master_url = base_url+base_addon+space_id+end_masterurl


t = urllib.request.urlopen(master_url).read().decode('utf-8')
master_playlist = re.findall(".*m3u8$",t,re.MULTILINE)
for i in master_playlist:
    master_playlist = i
print(master_playlist)


chunk_m3u8 = base_url+master_playlist
print(chunk_m3u8)

t = urllib.request.urlopen(chunk_m3u8).read().decode('utf-8')
t = t.replace('chunk', base_url+base_addon+space_id+end_chunkurl)

space_date = (re.search('\d{4}-\d{2}-\d{2}',t)).group()
filename = f'{space_id}.m3u8'
output = f'{space_date}[{space_id}].aac'
command = f"ffmpeg -protocol_whitelist file,https,tls,tcp -i {filename} -c copy {output}"

f = open(filename, 'x')
f.write(t)
f.close
os.system(command)


os.remove(filename)