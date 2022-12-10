#!/usr/bin/python
import os
import requests
import re
import sys


args = ' '.join(map(str,(sys.argv[1:])))
if len(args) == 0:
    print ('provide stream name or master/dynamic url and optionally space ID for metadata like spacename and host')

stream_name = re.search("[A-Za-z0-9\_\-]{86}", args).group()
space_id = re.search("1[A-Za-z]{12}", args)
#print ((stream_name),"\n",(space_id))
'''
base_url = 'https://canary-video-us-east-1.pscp.tv'
base_addon = '/Transcoding/v1/hls/'

end_masterurl = "/non_transcode/us-east-1/periscope-replay-direct-prod-us-east-1-public/audio-space/master_playlist.m3u8"
end_chunkurl = '/non_transcode/ap-northeast-1/periscope-replay-direct-prod-ap-northeast-1-public/audio-space/chunk'
master_url = base_url+base_addon+stream_name+end_masterurl
print(master_url)
'''
t = requests.get(master_url).text
master_playlist = re.findall(".*m3u8$",t,re.MULTILINE)
for i in master_playlist:
    master_playlist = i
print(master_playlist)


chunk_m3u8 = base_url+master_playlist
print(chunk_m3u8)

t = requests.get(chunk_m3u8).text

print (t.splitlines()[-2])
#if t.splitlines()[-1]

t = t.replace('chunk', base_url+base_addon+stream_name+end_chunkurl)

space_date = (re.search('\d{4}-\d{2}-\d{2}',t)).group()
filename = f'{stream_name}.m3u8'
output = f'{space_date}[{stream_name}].aac'
command = f"ffmpeg -protocol_whitelist file,https,tls,tcp -threads 12 -i {filename} -c copy {output}"

f = open(filename, 'x')
f.write(t)
f.close
#os.system(command)


#os.remove(filename)