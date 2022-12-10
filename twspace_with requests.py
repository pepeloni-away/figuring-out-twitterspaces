#!/usr/bin/python
import os
import subprocess
import requests
import re
import sys


args = ' '.join(map(str, (sys.argv[1:])))

try:
    stream_name = re.search('[A-Za-z0-9\_\-]{86}', args).group()
except AttributeError:
    print('Provide the 86 character long stream name or master/dynamic url that contains it and optionally space ID for metadata like space name and host')
    sys.exit(1)

try:
    space_id = re.search("1[A-Za-z]{12}", args).group()
except AttributeError:
    print('no space ID given, file wont have metadata')
    space_id = None


base_url = 'https://canary-video-us-east-1.pscp.tv'  # doesn't seem like this needs to match the server for audio fragments
servers = [
    f"https://prod-fastly-ap-northeast-1.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/ap-northeast-1/periscope-replay-direct-prod-ap-northeast-1-public/audio-space/master_playlist.m3u8",
    f"https://prod-fastly-ap-southeast-1.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/ap-southeast-1/periscope-replay-direct-prod-ap-southeast-1-public/audio-space/master_playlist.m3u8",
    f"https://prod-fastly-ap-southeast-2.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/ap-southeast-2/periscope-replay-direct-prod-ap-southeast-2-public/audio-space/master_playlist.m3u8",

    f"https://prod-fastly-eu-west-3.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/eu-west-3/periscope-replay-direct-prod-eu-west-3-public/audio-space/master_playlist.m3u8",
    f"https://prod-fastly-eu-west-3.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/eu-west-3/periscope-replay-direct-prod-eu-west-3-public/audio-space/master_playlist.m3u8",

    f"https://prod-fastly-us-east-1.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/us-east-1/periscope-replay-direct-prod-us-east-1-public/audio-space/master_playlist.m3u8"

]  # can't find more than these, add in the future?



if space_id is not None:
    params = {
                "variables": (
                    "{"
                    f'"id":"{space_id}",'
                    '"isMetatagsQuery":false,'
                    '"withSuperFollowsUserFields":false,'
                    '"withUserResults":true,'
                    '"withBirdwatchPivots":false,'
                    '"withReactionsMetadata":false,'
                    '"withReactionsPerspective":false,'
                    '"withSuperFollowsTweetFields":false,'
                    '"withReplays":true,'
                    '"withScheduledSpaces":true'
                    "}"
                )
    }
    headers = {
                "authorization": (
                    "Bearer "
                    "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
                    "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
                ),
                "x-guest-token": requests.post('https://api.twitter.com/1.1/guest/activate.json', headers={'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',}).json()["guest_token"],
    }
    response = requests.get(
            "https://twitter.com/i/api/graphql/jyQ0_DEMZHeoluCgHJ-U5Q/AudioSpaceById",
            params=params,
            headers=headers,
    ).json()
    print(response)














master_playlist = None
for sv in servers:
    while master_playlist is None:
        master_playlist = re.search('\/Transcoding.*\.m3u8', requests.get(sv).text).group()
        current_server = sv

print(master_playlist)

playlist_longtimestamp = re.search('playlist_\d{20}', master_playlist).group()
print(playlist_longtimestamp)

dl_playlist = current_server.replace('master_playlist', playlist_longtimestamp)
print (dl_playlist)
#chunk_m3u8 = base_url + master_playlist
# print(chunk_m3u8)


t = requests.get(dl_playlist).text

#print(t.splitlines()[-2])
# if t.splitlines()[-1]

#t = t.replace('chunk', current_server.replace('master_playlist.m3u8', 'chunk'))

space_date = (re.search('\d{4}-\d{2}-\d{2}', t)).group()
filename = f'{stream_name}.m3u8'
output = f'{space_date}[{stream_name}].aac'
# command = f"ffmpeg -protocol_whitelist file,https,tls,tcp -threads 12 -i {filename} -c copy {output}"
#command = ['ffmpeg', '-protocol_whitelist', 'file,https,tls,tcp', '-threads', '12', '-i', f'{filename}', '-c', 'copy',
#          f'{output}']
           
command = ['ffmpeg', '-i', f'{dl_playlist}', '-c', 'copy', '-threads', '22',
           f'{output}']


#try:
#    f = open(filename, 'x')
#    f.write(t)
#    f.close()
#except FileExistsError:
#    pass
#
print(command)
subprocess.run(command)

#os.remove(filename)
